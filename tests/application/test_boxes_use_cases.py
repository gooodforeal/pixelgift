import uuid
from datetime import datetime, timezone

import pytest

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
from src.application.use_cases.boxes import (
    AddBoxItemUseCase,
    ArchiveBoxUseCase,
    CreateBoxUseCase,
    PublishBoxUseCase,
    RemoveBoxItemUseCase,
    ReorderBoxItemsUseCase,
    UnarchiveBoxUseCase,
    UpdateBoxItemUseCase,
    UpdateBoxUseCase,
)
from src.domain.aggregates.boxes import MAX_BOX_ITEMS, Box, BoxStatus
from src.domain.entities.box_designs import BoxDesign
from src.domain.entities.box_items import BoxItemType
from src.domain.entities.media_files import MediaFile, MediaKind
from src.domain.exceptions.boxes import (
    BoxAccessDeniedError,
    BoxAlreadyArchivedError,
    BoxAlreadyOpenedError,
    BoxDesignNotAvailableError,
    BoxNotEditableError,
    BoxItemsLimitExceededError,
    BoxNotFoundError,
    BoxNotPublishableError,
    BoxWithoutItemsError,
    PublicSlugAlreadyTakenError,
)
from src.domain.exceptions.media_files import (
    MediaFileAccessDeniedError,
    MediaFileNotFoundError,
)
from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_design_name import BoxDesignName
from src.domain.values.box_item_caption import BoxItemCaption
from src.domain.values.box_message import BoxMessage
from src.domain.values.box_preview_title import BoxPreviewTitle
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle
from src.domain.values.public_slug import PublicSlug
from src.domain.values.url import Url
from tests.application.fakes import InMemoryUnitOfWork


def _design(*, is_active: bool = True) -> BoxDesign:
    return BoxDesign(
        code=f"design-{uuid.uuid4().hex[:8]}",
        name=BoxDesignName("Romantic"),
        preview_image_url=Url("https://example.com/design.png"),
        is_active=is_active,
    )


def _create_command(
    *,
    owner_id: uuid.UUID,
    design_id: uuid.UUID,
    activates_at: ActivatesAt,
    public_slug: PublicSlug | None = None,
) -> CreateBoxCommand:
    return CreateBoxCommand(
        owner_id=owner_id,
        design_id=design_id,
        title=BoxTitle("Happy birthday"),
        recipient_name=BoxRecipientName("Маша"),
        activates_at=activates_at,
        public_slug=public_slug,
        message=BoxMessage("For you"),
        preview_title=BoxPreviewTitle("Soon"),
    )


class TestCreateBoxUseCase:
    async def test_creates_draft_with_generated_slug(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        design = _design()
        await uow.box_designs.add(design)

        box = await CreateBoxUseCase(uow).execute(
            _create_command(
                owner_id=user_id,
                design_id=design.id,
                activates_at=activates_at,
            )
        )

        assert box.status == BoxStatus.DRAFT
        assert box.owner_id == user_id
        assert box.design_id == design.id
        assert box.public_slug.value
        assert uow.committed is True
        assert await uow.boxes.get_by_id(box.id) is box

    async def test_uses_provided_slug(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        design = _design()
        await uow.box_designs.add(design)
        slug = PublicSlug("gift-for-masha")

        box = await CreateBoxUseCase(uow).execute(
            _create_command(
                owner_id=user_id,
                design_id=design.id,
                activates_at=activates_at,
                public_slug=slug,
            )
        )

        assert box.public_slug == slug

    async def test_rejects_taken_slug(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        design = _design()
        await uow.box_designs.add(design)
        slug = PublicSlug("taken-slug")
        await CreateBoxUseCase(uow).execute(
            _create_command(
                owner_id=user_id,
                design_id=design.id,
                activates_at=activates_at,
                public_slug=slug,
            )
        )
        uow.committed = False

        with pytest.raises(PublicSlugAlreadyTakenError):
            await CreateBoxUseCase(uow).execute(
                _create_command(
                    owner_id=user_id,
                    design_id=design.id,
                    activates_at=activates_at,
                    public_slug=slug,
                )
            )

    async def test_rejects_missing_design(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()

        with pytest.raises(BoxDesignNotAvailableError):
            await CreateBoxUseCase(uow).execute(
                _create_command(
                    owner_id=user_id,
                    design_id=uuid.uuid4(),
                    activates_at=activates_at,
                )
            )

    async def test_rejects_inactive_design(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        design = _design(is_active=False)
        await uow.box_designs.add(design)

        with pytest.raises(BoxDesignNotAvailableError):
            await CreateBoxUseCase(uow).execute(
                _create_command(
                    owner_id=user_id,
                    design_id=design.id,
                    activates_at=activates_at,
                )
            )


class TestUpdateBoxUseCase:
    async def _seed_box(
        self,
        uow: InMemoryUnitOfWork,
        *,
        owner_id: uuid.UUID,
        activates_at: ActivatesAt,
        status: BoxStatus = BoxStatus.DRAFT,
    ) -> tuple[Box, BoxDesign]:
        design = _design()
        await uow.box_designs.add(design)
        box = await CreateBoxUseCase(uow).execute(
            _create_command(
                owner_id=owner_id,
                design_id=design.id,
                activates_at=activates_at,
                public_slug=PublicSlug(f"box-{uuid.uuid4().hex[:8]}"),
            )
        )
        box.status = status
        await uow.boxes.update(box)
        uow.committed = False
        return box, design

    async def test_updates_editable_fields(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box, _ = await self._seed_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        new_design = _design()
        await uow.box_designs.add(new_design)

        updated = await UpdateBoxUseCase(uow).execute(
            UpdateBoxCommand(
                box_id=box.id,
                actor_id=user_id,
                design_id=new_design.id,
                title=BoxTitle("Updated title"),
                recipient_name=BoxRecipientName("Катя"),
                activates_at=activates_at,
                timezone="Europe/Moscow",
                message=BoxMessage("Updated message"),
                preview_title=BoxPreviewTitle("New preview"),
                preview_image_url=Url("https://example.com/preview.png"),
            )
        )

        assert updated.design_id == new_design.id
        assert updated.title.value == "Updated title"
        assert updated.recipient_name.value == "Катя"
        assert updated.timezone == "Europe/Moscow"
        assert updated.message is not None
        assert updated.message.value == "Updated message"
        assert updated.preview_title is not None
        assert updated.preview_title.value == "New preview"
        assert uow.committed is True

    async def test_allows_scheduled_box(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box, design = await self._seed_box(
            uow,
            owner_id=user_id,
            activates_at=activates_at,
            status=BoxStatus.SCHEDULED,
        )

        updated = await UpdateBoxUseCase(uow).execute(
            UpdateBoxCommand(
                box_id=box.id,
                actor_id=user_id,
                design_id=design.id,
                title=BoxTitle("Still editable"),
                recipient_name=BoxRecipientName("Маша"),
                activates_at=activates_at,
            )
        )

        assert updated.title.value == "Still editable"

    async def test_rejects_foreign_owner(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box, design = await self._seed_box(
            uow, owner_id=user_id, activates_at=activates_at
        )

        with pytest.raises(BoxAccessDeniedError):
            await UpdateBoxUseCase(uow).execute(
                UpdateBoxCommand(
                    box_id=box.id,
                    actor_id=uuid.uuid4(),
                    design_id=design.id,
                    title=BoxTitle("Hack"),
                    recipient_name=BoxRecipientName("X"),
                    activates_at=activates_at,
                )
            )

    async def test_rejects_missing_box(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        design = _design()
        await uow.box_designs.add(design)

        with pytest.raises(BoxNotFoundError):
            await UpdateBoxUseCase(uow).execute(
                UpdateBoxCommand(
                    box_id=uuid.uuid4(),
                    actor_id=user_id,
                    design_id=design.id,
                    title=BoxTitle("Missing"),
                    recipient_name=BoxRecipientName("X"),
                    activates_at=activates_at,
                )
            )

    async def test_rejects_active_box(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box, design = await self._seed_box(
            uow,
            owner_id=user_id,
            activates_at=activates_at,
            status=BoxStatus.ACTIVE,
        )

        with pytest.raises(BoxNotEditableError):
            await UpdateBoxUseCase(uow).execute(
                UpdateBoxCommand(
                    box_id=box.id,
                    actor_id=user_id,
                    design_id=design.id,
                    title=BoxTitle("Too late"),
                    recipient_name=BoxRecipientName("X"),
                    activates_at=activates_at,
                )
            )

    async def test_rejects_inactive_design_on_update(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box, _ = await self._seed_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        inactive = _design(is_active=False)
        await uow.box_designs.add(inactive)

        with pytest.raises(BoxDesignNotAvailableError):
            await UpdateBoxUseCase(uow).execute(
                UpdateBoxCommand(
                    box_id=box.id,
                    actor_id=user_id,
                    design_id=inactive.id,
                    title=BoxTitle("Bad design"),
                    recipient_name=BoxRecipientName("X"),
                    activates_at=activates_at,
                )
            )


def _media_file(*, owner_id: uuid.UUID, kind: MediaKind = MediaKind.IMAGE) -> MediaFile:
    return MediaFile(
        owner_id=owner_id,
        storage_key=f"uploads/{uuid.uuid4().hex}.bin",
        mime_type="image/png",
        media_kind=kind,
        size_bytes=1024,
    )


async def _seed_editable_box(
    uow: InMemoryUnitOfWork,
    *,
    owner_id: uuid.UUID,
    activates_at: ActivatesAt,
) -> Box:
    design = _design()
    await uow.box_designs.add(design)
    box = await CreateBoxUseCase(uow).execute(
        _create_command(
            owner_id=owner_id,
            design_id=design.id,
            activates_at=activates_at,
            public_slug=PublicSlug(f"fill-{uuid.uuid4().hex[:8]}"),
        )
    )
    uow.committed = False
    return box


class TestAddBoxItemUseCase:
    async def test_adds_item_from_owned_media(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        media = _media_file(owner_id=user_id, kind=MediaKind.VIDEO)
        await uow.media_files.add(media)

        updated = await AddBoxItemUseCase(uow).execute(
            AddBoxItemCommand(
                box_id=box.id,
                actor_id=user_id,
                media_file_id=media.id,
                caption=BoxItemCaption("Trip"),
            )
        )

        assert len(updated.items) == 1
        assert updated.items[0].media_file_id == media.id
        assert updated.items[0].item_type == BoxItemType.VIDEO
        assert updated.items[0].sort_order.value == 1
        assert updated.items[0].caption is not None
        assert updated.items[0].caption.value == "Trip"
        assert uow.committed is True

    async def test_adds_text_item_without_media(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )

        updated = await AddBoxItemUseCase(uow).execute(
            AddBoxItemCommand(
                box_id=box.id,
                actor_id=user_id,
                item_type="text",
                caption=BoxItemCaption("Просто текст"),
            )
        )

        assert len(updated.items) == 1
        assert updated.items[0].media_file_id is None
        assert updated.items[0].item_type == BoxItemType.TEXT
        assert updated.items[0].caption is not None
        assert updated.items[0].caption.value == "Просто текст"
        assert uow.committed is True

    async def test_rejects_item_over_limit(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )

        for _ in range(MAX_BOX_ITEMS):
            await AddBoxItemUseCase(uow).execute(
                AddBoxItemCommand(
                    box_id=box.id,
                    actor_id=user_id,
                    item_type="text",
                    caption=BoxItemCaption("Карточка"),
                )
            )

        with pytest.raises(BoxItemsLimitExceededError):
            await AddBoxItemUseCase(uow).execute(
                AddBoxItemCommand(
                    box_id=box.id,
                    actor_id=user_id,
                    item_type="text",
                    caption=BoxItemCaption("Лишняя"),
                )
            )

    async def test_rejects_missing_media(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )

        with pytest.raises(MediaFileNotFoundError):
            await AddBoxItemUseCase(uow).execute(
                AddBoxItemCommand(
                    box_id=box.id,
                    actor_id=user_id,
                    media_file_id=uuid.uuid4(),
                )
            )

    async def test_rejects_foreign_media(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        media = _media_file(owner_id=uuid.uuid4())
        await uow.media_files.add(media)

        with pytest.raises(MediaFileAccessDeniedError):
            await AddBoxItemUseCase(uow).execute(
                AddBoxItemCommand(
                    box_id=box.id,
                    actor_id=user_id,
                    media_file_id=media.id,
                )
            )


class TestUpdateRemoveReorderBoxItemsUseCases:
    async def test_update_remove_and_reorder(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        first_media = _media_file(owner_id=user_id, kind=MediaKind.IMAGE)
        second_media = _media_file(owner_id=user_id, kind=MediaKind.GIF)
        third_media = _media_file(owner_id=user_id, kind=MediaKind.VOICE)
        await uow.media_files.add(first_media)
        await uow.media_files.add(second_media)
        await uow.media_files.add(third_media)

        box = await AddBoxItemUseCase(uow).execute(
            AddBoxItemCommand(
                box_id=box.id, actor_id=user_id, media_file_id=first_media.id
            )
        )
        box = await AddBoxItemUseCase(uow).execute(
            AddBoxItemCommand(
                box_id=box.id, actor_id=user_id, media_file_id=second_media.id
            )
        )
        box = await AddBoxItemUseCase(uow).execute(
            AddBoxItemCommand(
                box_id=box.id, actor_id=user_id, media_file_id=third_media.id
            )
        )
        first, second, third = box.items

        box = await UpdateBoxItemUseCase(uow).execute(
            UpdateBoxItemCommand(
                box_id=box.id,
                actor_id=user_id,
                item_id=second.id,
                caption=BoxItemCaption("Middle"),
            )
        )
        assert box.items[1].caption is not None
        assert box.items[1].caption.value == "Middle"

        box = await ReorderBoxItemsUseCase(uow).execute(
            ReorderBoxItemsCommand(
                box_id=box.id,
                actor_id=user_id,
                item_ids=(third.id, first.id, second.id),
            )
        )
        assert [item.id for item in box.items] == [third.id, first.id, second.id]
        assert [item.sort_order.value for item in box.items] == [1, 2, 3]

        box = await RemoveBoxItemUseCase(uow).execute(
            RemoveBoxItemCommand(
                box_id=box.id,
                actor_id=user_id,
                item_id=first.id,
            )
        )
        assert [item.id for item in box.items] == [third.id, second.id]
        assert [item.sort_order.value for item in box.items] == [1, 2]


class TestPublishAndArchiveBoxUseCases:
    async def test_publishes_draft_with_items(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        media = _media_file(owner_id=user_id)
        await uow.media_files.add(media)
        await AddBoxItemUseCase(uow).execute(
            AddBoxItemCommand(
                box_id=box.id, actor_id=user_id, media_file_id=media.id
            )
        )

        published = await PublishBoxUseCase(uow).execute(
            PublishBoxCommand(box_id=box.id, actor_id=user_id)
        )

        assert published.status == BoxStatus.SCHEDULED
        assert published.published_at is not None
        assert uow.committed is True

    async def test_rejects_publishing_empty_box(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )

        with pytest.raises(BoxWithoutItemsError):
            await PublishBoxUseCase(uow).execute(
                PublishBoxCommand(box_id=box.id, actor_id=user_id)
            )

    async def test_rejects_publishing_twice(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        media = _media_file(owner_id=user_id)
        await uow.media_files.add(media)
        await AddBoxItemUseCase(uow).execute(
            AddBoxItemCommand(
                box_id=box.id, actor_id=user_id, media_file_id=media.id
            )
        )
        await PublishBoxUseCase(uow).execute(
            PublishBoxCommand(box_id=box.id, actor_id=user_id)
        )

        with pytest.raises(BoxNotPublishableError):
            await PublishBoxUseCase(uow).execute(
                PublishBoxCommand(box_id=box.id, actor_id=user_id)
            )

    async def test_rejects_foreign_owner(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )

        with pytest.raises(BoxAccessDeniedError):
            await PublishBoxUseCase(uow).execute(
                PublishBoxCommand(box_id=box.id, actor_id=uuid.uuid4())
            )

    async def test_archives_box_once(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )

        archived = await ArchiveBoxUseCase(uow).execute(
            ArchiveBoxCommand(box_id=box.id, actor_id=user_id)
        )
        assert archived.status == BoxStatus.ARCHIVED

        with pytest.raises(BoxAlreadyArchivedError):
            await ArchiveBoxUseCase(uow).execute(
                ArchiveBoxCommand(box_id=box.id, actor_id=user_id)
            )

    async def test_unarchives_unpublished_to_draft(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        await ArchiveBoxUseCase(uow).execute(
            ArchiveBoxCommand(box_id=box.id, actor_id=user_id)
        )

        restored = await UnarchiveBoxUseCase(uow).execute(
            UnarchiveBoxCommand(box_id=box.id, actor_id=user_id)
        )

        assert restored.status == BoxStatus.DRAFT

    async def test_unarchives_published_to_scheduled(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        media = _media_file(owner_id=user_id)
        await uow.media_files.add(media)
        await AddBoxItemUseCase(uow).execute(
            AddBoxItemCommand(
                box_id=box.id, actor_id=user_id, media_file_id=media.id
            )
        )
        await PublishBoxUseCase(uow).execute(
            PublishBoxCommand(box_id=box.id, actor_id=user_id)
        )
        await ArchiveBoxUseCase(uow).execute(
            ArchiveBoxCommand(box_id=box.id, actor_id=user_id)
        )

        restored = await UnarchiveBoxUseCase(uow).execute(
            UnarchiveBoxCommand(box_id=box.id, actor_id=user_id)
        )

        assert restored.status == BoxStatus.SCHEDULED
        assert restored.published_at is not None

    async def test_rejects_unarchive_after_open(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ):
        uow = InMemoryUnitOfWork()
        box = await _seed_editable_box(
            uow, owner_id=user_id, activates_at=activates_at
        )
        box.first_opened_at = datetime(2026, 6, 2, tzinfo=timezone.utc)
        box.status = BoxStatus.ARCHIVED
        await uow.boxes.update(box)

        with pytest.raises(BoxAlreadyOpenedError):
            await UnarchiveBoxUseCase(uow).execute(
                UnarchiveBoxCommand(box_id=box.id, actor_id=user_id)
            )
