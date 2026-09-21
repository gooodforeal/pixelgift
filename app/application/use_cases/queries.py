from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import uuid

import jwt

from app.application.dto.media import MediaContent
from app.application.ports.storage.base import BaseObjectStorage
from app.application.ports.queues.base import BaseTaskQueue
from app.application.services.jwt import JwtService
from app.application.uow.base import BaseUnitOfWork
from app.application.use_cases.notifications import schedule_owner_notification_job
from app.domain.aggregates.boxes import Box
from app.domain.entities.box_designs import BoxDesign
from app.domain.entities.notification_jobs import NotificationTemplate
from app.domain.entities.users import User
from app.domain.exceptions.auth import UserInactiveError
from app.domain.exceptions.boxes import (
    BoxAccessDeniedError,
    BoxContentLockedError,
    BoxItemNotFoundError,
    BoxNotFoundBySlugError,
    BoxNotFoundError,
    BoxUnlockNotYetAvailableError,
    BoxUnlockPasswordIncorrectError,
)
from app.domain.exceptions.media_files import MediaFileNotFoundError
from app.domain.exceptions.users import UserNotFoundError
from app.domain.values.public_slug import PublicSlug

_HIDDEN_STATUSES = frozenset({"draft", "archived"})
logger = logging.getLogger(__name__)


async def _kick_notification_dispatch(task_queue: BaseTaskQueue | None) -> None:
    if task_queue is None:
        return
    try:
        await task_queue.kick_notification_dispatch()
    except Exception:
        logger.exception("Failed to kick notification dispatch")


@dataclass(frozen=True, kw_only=True)
class PublicBoxView:
    box: Box
    content_unlocked: bool
    design: BoxDesign | None = None
    unlock_token: str | None = None


def _token_unlocks_box(
    jwt_service: JwtService | None,
    *,
    box: Box,
    unlock_token: str | None,
) -> bool:
    if box.unlock_password is None:
        return True
    if not unlock_token or jwt_service is None:
        return False
    try:
        payload = jwt_service.decode_box_unlock_token(unlock_token)
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return False
    return payload.box_id == box.id and payload.public_slug == box.public_slug.value


@dataclass(frozen=True, kw_only=True)
class BoxesPage:
    items: list[Box]
    total: int
    page: int
    page_size: int
    status_counts: dict[str, int]


class GetBoxUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, box_id: uuid.UUID, actor_id: uuid.UUID) -> Box:
        async with self._uow as uow:
            box = await uow.boxes.get_by_id(box_id)
            if box is None:
                raise BoxNotFoundError(box_id)
            if box.owner_id != actor_id:
                raise BoxAccessDeniedError(box_id, actor_id)
            if box.activate_if_due():
                box = await uow.boxes.update(box)
                await uow.commit()
            return box


class ListBoxesUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        owner_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
    ) -> BoxesPage:
        offset = (page - 1) * page_size
        async with self._uow as uow:
            boxes = await uow.boxes.list_by_owner_id(
                owner_id,
                limit=page_size,
                offset=offset,
            )
            changed = False
            for box in boxes:
                if box.activate_if_due():
                    await uow.boxes.update(box)
                    changed = True

            total = await uow.boxes.count_by_owner_id(owner_id)
            status_counts = await uow.boxes.count_statuses_by_owner_id(owner_id)
            if changed:
                await uow.commit()
            return BoxesPage(
                items=boxes,
                total=total,
                page=page,
                page_size=page_size,
                status_counts=status_counts,
            )


class GetPublicBoxUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        storage: BaseObjectStorage | None = None,
        task_queue: BaseTaskQueue | None = None,
        jwt_service: JwtService | None = None,
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._task_queue = task_queue
        self._jwt = jwt_service

    async def execute(
        self,
        *,
        public_slug: str,
        unlock_token: str | None = None,
    ) -> PublicBoxView:
        slug = PublicSlug(public_slug)
        async with self._uow as uow:
            box = await uow.boxes.get_by_public_slug(slug)
            if box is None:
                raise BoxNotFoundBySlugError(public_slug)

            if box.status.value in _HIDDEN_STATUSES:
                raise BoxNotFoundBySlugError(public_slug)

            now = datetime.now(timezone.utc)
            timer_ready = box.activates_at.value <= now
            password_ok = _token_unlocks_box(
                self._jwt, box=box, unlock_token=unlock_token
            )
            unlocked = timer_ready and password_ok
            just_opened = False

            if unlocked and box.first_opened_at is None:
                just_opened = box.mark_opened(now=now)
                if just_opened:
                    await uow.boxes.update(box)
                    await schedule_owner_notification_job(
                        uow,
                        box_id=box.id,
                        template=NotificationTemplate.BOX_OPENED,
                        at=box.first_opened_at,
                    )
                    await uow.commit()
            elif box.activate_if_due(now=now):
                await uow.boxes.update(box)
                await uow.commit()

            design = await uow.box_designs.get_by_id(box.design_id)
            view = PublicBoxView(box=box, content_unlocked=unlocked, design=design)
            should_kick = just_opened

        if should_kick:
            await _kick_notification_dispatch(self._task_queue)
        return view


class UnlockPublicBoxUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        jwt_service: JwtService,
        task_queue: BaseTaskQueue | None = None,
    ) -> None:
        self._uow = uow
        self._jwt = jwt_service
        self._task_queue = task_queue

    async def execute(self, *, public_slug: str, password: str) -> PublicBoxView:
        slug = PublicSlug(public_slug)
        async with self._uow as uow:
            box = await uow.boxes.get_by_public_slug(slug)
            if box is None or box.status.value in _HIDDEN_STATUSES:
                raise BoxNotFoundBySlugError(public_slug)

            now = datetime.now(timezone.utc)
            if box.activates_at.value > now:
                raise BoxUnlockNotYetAvailableError(public_slug)

            if box.unlock_password is None:
                token = None
                unlocked = True
            elif box.unlock_password.value != password:
                raise BoxUnlockPasswordIncorrectError(public_slug)
            else:
                token = self._jwt.create_box_unlock_token(
                    box_id=box.id,
                    public_slug=box.public_slug.value,
                )
                unlocked = True

            just_opened = False
            if unlocked and box.first_opened_at is None:
                just_opened = box.mark_opened(now=now)
                if just_opened:
                    await uow.boxes.update(box)
                    await schedule_owner_notification_job(
                        uow,
                        box_id=box.id,
                        template=NotificationTemplate.BOX_OPENED,
                        at=box.first_opened_at,
                    )
                    await uow.commit()
            elif box.activate_if_due(now=now):
                await uow.boxes.update(box)
                await uow.commit()

            design = await uow.box_designs.get_by_id(box.design_id)
            view = PublicBoxView(
                box=box,
                content_unlocked=unlocked,
                design=design,
                unlock_token=token,
            )
            should_kick = just_opened

        if should_kick:
            await _kick_notification_dispatch(self._task_queue)
        return view


class GetPublicBoxItemContentUseCase:
    """Streams media of an unlocked public box — no authentication required."""

    def __init__(
        self,
        uow: BaseUnitOfWork,
        storage: BaseObjectStorage,
        jwt_service: JwtService | None = None,
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._jwt = jwt_service

    async def execute(
        self,
        *,
        public_slug: str,
        item_id: uuid.UUID,
        unlock_token: str | None = None,
    ) -> MediaContent:
        slug = PublicSlug(public_slug)
        async with self._uow as uow:
            box = await uow.boxes.get_by_public_slug(slug)
            if box is None or box.status.value in _HIDDEN_STATUSES:
                raise BoxNotFoundBySlugError(public_slug)

            if box.activates_at.value > datetime.now(timezone.utc):
                raise BoxContentLockedError(public_slug)

            if not _token_unlocks_box(self._jwt, box=box, unlock_token=unlock_token):
                raise BoxContentLockedError(public_slug)

            item = next((i for i in box.items if i.id == item_id), None)
            if item is None:
                raise BoxItemNotFoundError(item_id)
            if item.item_type.value == "text" or item.media_file_id is None:
                raise BoxItemNotFoundError(item_id)

            media = await uow.media_files.get_by_id(item.media_file_id)
            if media is None:
                raise MediaFileNotFoundError(item.media_file_id)

        data = await self._storage.download(media.storage_key)
        return MediaContent(
            data=data,
            mime_type=media.mime_type,
            filename=media.original_filename,
        )


class GetUserAvatarUseCase:
    def __init__(self, uow: BaseUnitOfWork, storage: BaseObjectStorage) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(self, *, user_id: uuid.UUID) -> MediaContent:
        from app.application.use_cases.auth import avatar_storage_key

        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None or user.photo_url is None:
                raise UserNotFoundError(user_id)

        data = await self._storage.download(avatar_storage_key(user_id))
        return MediaContent(
            data=data,
            mime_type="image/jpeg",
            filename=f"{user_id}.jpg",
        )


class GetCurrentUserUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, user_id: uuid.UUID) -> User:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(user_id)
            if not user.is_active:
                raise UserInactiveError(user_id)
            return user
