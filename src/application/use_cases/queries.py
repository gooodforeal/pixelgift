from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from src.application.dto.media import MediaContent
from src.application.ports.storage.base import BaseObjectStorage
from src.application.uow.base import BaseUnitOfWork
from src.domain.aggregates.boxes import Box
from src.domain.entities.box_designs import BoxDesign
from src.domain.entities.users import User
from src.domain.exceptions.auth import UserInactiveError
from src.domain.exceptions.boxes import (
    BoxAccessDeniedError,
    BoxContentLockedError,
    BoxItemNotFoundError,
    BoxNotFoundBySlugError,
    BoxNotFoundError,
)
from src.domain.exceptions.media_files import MediaFileNotFoundError
from src.domain.exceptions.users import UserNotFoundError
from src.domain.values.public_slug import PublicSlug

_HIDDEN_STATUSES = frozenset({"draft", "archived"})


@dataclass(frozen=True, kw_only=True)
class PublicBoxView:
    box: Box
    content_unlocked: bool
    design: BoxDesign | None = None


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
            return box


class ListBoxesUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, owner_id: uuid.UUID) -> list[Box]:
        async with self._uow as uow:
            return await uow.boxes.list_by_owner_id(owner_id)


class GetPublicBoxUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        storage: BaseObjectStorage | None = None,
    ) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(self, *, public_slug: str) -> PublicBoxView:
        slug = PublicSlug(public_slug)
        async with self._uow as uow:
            box = await uow.boxes.get_by_public_slug(slug)
            if box is None:
                raise BoxNotFoundBySlugError(public_slug)

            if box.status.value in _HIDDEN_STATUSES:
                raise BoxNotFoundBySlugError(public_slug)

            now = datetime.now(timezone.utc)
            unlocked = box.activates_at.value <= now

            if unlocked and box.first_opened_at is None:
                from src.domain.aggregates.boxes import BoxStatus

                box.first_opened_at = now
                if box.status == BoxStatus.SCHEDULED:
                    box.status = BoxStatus.ACTIVE
                await uow.boxes.update(box)
                await uow.commit()

            design = await uow.box_designs.get_by_id(box.design_id)
            return PublicBoxView(box=box, content_unlocked=unlocked, design=design)


class GetPublicBoxItemContentUseCase:
    """Streams media of an unlocked public box — no authentication required."""

    def __init__(self, uow: BaseUnitOfWork, storage: BaseObjectStorage) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(
        self,
        *,
        public_slug: str,
        item_id: uuid.UUID,
    ) -> MediaContent:
        slug = PublicSlug(public_slug)
        async with self._uow as uow:
            box = await uow.boxes.get_by_public_slug(slug)
            if box is None or box.status.value in _HIDDEN_STATUSES:
                raise BoxNotFoundBySlugError(public_slug)

            if box.activates_at.value > datetime.now(timezone.utc):
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
        from src.application.use_cases.auth import avatar_storage_key

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
