from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from src.application.ports.storage.base import BaseObjectStorage
from src.application.uow.base import BaseUnitOfWork
from src.domain.aggregates.boxes import Box
from src.domain.exceptions.boxes import (
    BoxAccessDeniedError,
    BoxNotFoundBySlugError,
    BoxNotFoundError,
)
from src.domain.values.public_slug import PublicSlug


@dataclass(frozen=True, kw_only=True)
class PublicBoxView:
    box: Box
    content_unlocked: bool


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

            if box.status.value in {"draft", "archived"}:
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

            return PublicBoxView(box=box, content_unlocked=unlocked)
