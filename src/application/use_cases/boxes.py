import secrets
import uuid

from src.application.dto.boxes import (
    AddBoxItemCommand,
    ArchiveBoxCommand,
    CreateBoxCommand,
    PublishBoxCommand,
    RemoveBoxItemCommand,
    ReorderBoxItemsCommand,
    UnarchiveBoxCommand,
    UpdateBoxCommand,
    UpdateBoxItemCommand,
)
from src.application.uow.base import BaseUnitOfWork
from src.application.use_cases.notifications import sync_gift_ready_job
from src.domain.aggregates.boxes import Box, BoxStatus
from src.domain.entities.box_items import BoxItemType
from src.domain.entities.media_files import MediaKind
from src.domain.exceptions.box_items import BoxItemInvalidError
from src.domain.exceptions.boxes import (
    BoxAccessDeniedError,
    BoxDesignNotAvailableError,
    BoxNotEditableError,
    BoxNotFoundError,
    PublicSlugAlreadyTakenError,
)
from src.domain.exceptions.media_files import (
    MediaFileAccessDeniedError,
    MediaFileNotFoundError,
)
from src.domain.values.public_slug import PublicSlug


_EDITABLE_STATUSES = frozenset({BoxStatus.DRAFT, BoxStatus.SCHEDULED})
_SLUG_GENERATE_ATTEMPTS = 5


def generate_public_slug() -> PublicSlug:
    return PublicSlug(secrets.token_hex(8))


def _item_type_from_media_kind(media_kind: MediaKind) -> BoxItemType:
    return BoxItemType(media_kind.value)


async def _get_own_box(
    uow: BaseUnitOfWork,
    *,
    box_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> Box:
    box = await uow.boxes.get_by_id(box_id)
    if box is None:
        raise BoxNotFoundError(box_id)

    if box.owner_id != actor_id:
        raise BoxAccessDeniedError(box_id, actor_id)

    return box


async def _get_editable_box(
    uow: BaseUnitOfWork,
    *,
    box_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> Box:
    box = await _get_own_box(uow, box_id=box_id, actor_id=actor_id)

    if box.status not in _EDITABLE_STATUSES:
        raise BoxNotEditableError(box_id, box.status)

    return box


class CreateBoxUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: CreateBoxCommand) -> Box:
        async with self._uow as uow:
            await self._ensure_design_available(uow, command.design_id)
            public_slug = await self._resolve_public_slug(uow, command.public_slug)

            box = Box(
                owner_id=command.owner_id,
                design_id=command.design_id,
                public_slug=public_slug,
                title=command.title,
                recipient_name=command.recipient_name,
                activates_at=command.activates_at,
                status=BoxStatus.DRAFT,
                timezone=command.timezone,
                recipient_email=command.recipient_email,
                message=command.message,
                preview_title=command.preview_title,
                preview_image_url=command.preview_image_url,
            )
            await uow.boxes.add(box)
            await uow.commit()
            return box

    async def _ensure_design_available(
        self,
        uow: BaseUnitOfWork,
        design_id: uuid.UUID,
    ) -> None:
        design = await uow.box_designs.get_by_id(design_id)
        if design is None or not design.is_active:
            raise BoxDesignNotAvailableError(design_id)

    async def _resolve_public_slug(
        self,
        uow: BaseUnitOfWork,
        public_slug: PublicSlug | None,
    ) -> PublicSlug:
        if public_slug is not None:
            existing = await uow.boxes.get_by_public_slug(public_slug)
            if existing is not None:
                raise PublicSlugAlreadyTakenError(public_slug.value)
            return public_slug

        for _ in range(_SLUG_GENERATE_ATTEMPTS):
            candidate = generate_public_slug()
            if await uow.boxes.get_by_public_slug(candidate) is None:
                return candidate

        raise PublicSlugAlreadyTakenError(candidate.value)


class UpdateBoxUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: UpdateBoxCommand) -> Box:
        async with self._uow as uow:
            box = await _get_editable_box(
                uow, box_id=command.box_id, actor_id=command.actor_id
            )

            design = await uow.box_designs.get_by_id(command.design_id)
            if design is None or not design.is_active:
                raise BoxDesignNotAvailableError(command.design_id)

            box.update_details(
                design_id=command.design_id,
                title=command.title,
                recipient_name=command.recipient_name,
                activates_at=command.activates_at,
                timezone=command.timezone,
                recipient_email=command.recipient_email,
                message=command.message,
                preview_title=command.preview_title,
                preview_image_url=command.preview_image_url,
            )
            updated = await uow.boxes.update(box)
            await sync_gift_ready_job(uow, updated)
            await uow.commit()
            return updated


class AddBoxItemUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: AddBoxItemCommand) -> Box:
        async with self._uow as uow:
            box = await _get_editable_box(
                uow, box_id=command.box_id, actor_id=command.actor_id
            )

            if command.item_type == BoxItemType.TEXT.value:
                if command.media_file_id is not None:
                    raise BoxItemInvalidError(
                        "Text item must not reference a media file"
                    )
                if command.caption is None:
                    raise BoxItemInvalidError("Text item requires non-empty text")
                box.add_item(
                    media_file_id=None,
                    item_type=BoxItemType.TEXT,
                    sort_order=command.sort_order,
                    caption=command.caption,
                    metadata=command.metadata,
                )
            elif command.item_type == BoxItemType.TOY.value:
                if command.media_file_id is not None:
                    raise BoxItemInvalidError(
                        "Toy item must not reference a media file"
                    )
                box.add_item(
                    media_file_id=None,
                    item_type=BoxItemType.TOY,
                    sort_order=command.sort_order,
                    caption=command.caption,
                    metadata=command.metadata,
                )
            elif command.item_type == BoxItemType.GEOPOINT.value:
                if command.media_file_id is not None:
                    raise BoxItemInvalidError(
                        "Geopoint item must not reference a media file"
                    )
                box.add_item(
                    media_file_id=None,
                    item_type=BoxItemType.GEOPOINT,
                    sort_order=command.sort_order,
                    caption=command.caption,
                    metadata=command.metadata,
                )
            elif command.item_type == BoxItemType.DRAWING.value:
                if command.media_file_id is None:
                    raise BoxItemInvalidError("Drawing item requires an image file")
                media_file = await uow.media_files.get_by_id(command.media_file_id)
                if media_file is None:
                    raise MediaFileNotFoundError(command.media_file_id)
                if media_file.owner_id != command.actor_id:
                    raise MediaFileAccessDeniedError(
                        command.media_file_id, command.actor_id
                    )
                if media_file.media_kind != MediaKind.IMAGE:
                    raise BoxItemInvalidError("Drawing item requires an image file")

                box.add_item(
                    media_file_id=media_file.id,
                    item_type=BoxItemType.DRAWING,
                    sort_order=command.sort_order,
                    caption=command.caption,
                    metadata=command.metadata,
                )
            elif command.item_type == BoxItemType.CIRCLE.value:
                if command.media_file_id is None:
                    raise BoxItemInvalidError("Circle item requires a video file")
                media_file = await uow.media_files.get_by_id(command.media_file_id)
                if media_file is None:
                    raise MediaFileNotFoundError(command.media_file_id)
                if media_file.owner_id != command.actor_id:
                    raise MediaFileAccessDeniedError(
                        command.media_file_id, command.actor_id
                    )
                if media_file.media_kind != MediaKind.VIDEO:
                    raise BoxItemInvalidError("Circle item requires a video file")

                box.add_item(
                    media_file_id=media_file.id,
                    item_type=BoxItemType.CIRCLE,
                    sort_order=command.sort_order,
                    caption=command.caption,
                    metadata=command.metadata,
                )
            else:
                if command.media_file_id is None:
                    raise BoxItemInvalidError("Media item requires a media file")
                media_file = await uow.media_files.get_by_id(command.media_file_id)
                if media_file is None:
                    raise MediaFileNotFoundError(command.media_file_id)
                if media_file.owner_id != command.actor_id:
                    raise MediaFileAccessDeniedError(
                        command.media_file_id, command.actor_id
                    )

                box.add_item(
                    media_file_id=media_file.id,
                    item_type=_item_type_from_media_kind(media_file.media_kind),
                    sort_order=command.sort_order,
                    caption=command.caption,
                    metadata=command.metadata,
                )

            updated = await uow.boxes.update(box)
            await uow.commit()
            return updated


class UpdateBoxItemUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: UpdateBoxItemCommand) -> Box:
        async with self._uow as uow:
            box = await _get_editable_box(
                uow, box_id=command.box_id, actor_id=command.actor_id
            )
            box.update_item(
                command.item_id,
                caption=command.caption,
                metadata=command.metadata,
            )
            updated = await uow.boxes.update(box)
            await uow.commit()
            return updated


class RemoveBoxItemUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: RemoveBoxItemCommand) -> Box:
        async with self._uow as uow:
            box = await _get_editable_box(
                uow, box_id=command.box_id, actor_id=command.actor_id
            )
            box.remove_item(command.item_id)
            updated = await uow.boxes.update(box)
            await uow.commit()
            return updated


class ReorderBoxItemsUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: ReorderBoxItemsCommand) -> Box:
        async with self._uow as uow:
            box = await _get_editable_box(
                uow, box_id=command.box_id, actor_id=command.actor_id
            )
            box.reorder_items(command.item_ids)
            updated = await uow.boxes.update(box)
            await uow.commit()
            return updated


class PublishBoxUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: PublishBoxCommand) -> Box:
        async with self._uow as uow:
            box = await _get_own_box(
                uow, box_id=command.box_id, actor_id=command.actor_id
            )
            box.publish()
            updated = await uow.boxes.update(box)
            await sync_gift_ready_job(uow, updated)
            await uow.commit()
            return updated


class ArchiveBoxUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: ArchiveBoxCommand) -> Box:
        async with self._uow as uow:
            box = await _get_own_box(
                uow, box_id=command.box_id, actor_id=command.actor_id
            )
            box.archive()
            updated = await uow.boxes.update(box)
            await sync_gift_ready_job(uow, updated)
            await uow.commit()
            return updated


class UnarchiveBoxUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: UnarchiveBoxCommand) -> Box:
        async with self._uow as uow:
            box = await _get_own_box(
                uow, box_id=command.box_id, actor_id=command.actor_id
            )
            box.unarchive()
            updated = await uow.boxes.update(box)
            await sync_gift_ready_job(uow, updated)
            await uow.commit()
            return updated
