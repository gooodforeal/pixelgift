import uuid
from datetime import datetime, timezone

import pytest

from src.domain.entities.box_items import BoxItemType
from src.domain.aggregates.boxes import Box, BoxStatus
from src.domain.exceptions.boxes import (
    BoxItemDuplicateSortOrderError,
    BoxItemNotFoundError,
    BoxItemReorderError,
)
from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_item_caption import BoxItemCaption
from src.domain.values.box_message import BoxMessage
from src.domain.values.box_preview_title import BoxPreviewTitle
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle
from src.domain.values.public_slug import PublicSlug
from src.domain.values.sort_order import SortOrder
from src.domain.values.url import Url


def _make_box(activates_at: ActivatesAt, **kwargs: object) -> Box:
    defaults: dict[str, object] = {
        "owner_id": uuid.uuid4(),
        "design_id": uuid.uuid4(),
        "public_slug": PublicSlug("gift-42"),
        "title": BoxTitle("Happy birthday"),
        "recipient_name": BoxRecipientName("Маша"),
        "activates_at": activates_at,
        "status": BoxStatus.DRAFT,
    }
    defaults.update(kwargs)
    return Box(**defaults)  # type: ignore[arg-type]


class TestBox:
    def test_create_minimal(self, activates_at: ActivatesAt):
        owner_id = uuid.uuid4()
        design_id = uuid.uuid4()

        box = _make_box(
            activates_at,
            owner_id=owner_id,
            design_id=design_id,
        )

        assert box.owner_id == owner_id
        assert box.design_id == design_id
        assert box.public_slug.value == "gift-42"
        assert box.status == BoxStatus.DRAFT
        assert box.timezone == "UTC"
        assert box.message is None
        assert box.preview_title is None
        assert box.items == []

    def test_create_with_optional_fields(self, activates_at: ActivatesAt):
        published = datetime(2026, 6, 1, tzinfo=timezone.utc)
        opened = datetime(2026, 6, 2, tzinfo=timezone.utc)

        box = _make_box(
            activates_at,
            public_slug=PublicSlug("summer"),
            title=BoxTitle("For you"),
            recipient_name=BoxRecipientName("Kate"),
            status=BoxStatus.SCHEDULED,
            timezone="Europe/Moscow",
            message=BoxMessage("Hello!"),
            preview_title=BoxPreviewTitle("Soon"),
            preview_image_url=Url("https://example.com/preview.png"),
            published_at=published,
            first_opened_at=opened,
        )

        assert box.timezone == "Europe/Moscow"
        assert box.message is not None
        assert box.message.value == "Hello!"
        assert box.published_at == published
        assert box.first_opened_at == opened

    def test_base_entity_fields(self, activates_at: ActivatesAt):
        box = _make_box(
            activates_at,
            public_slug=PublicSlug("a"),
            title=BoxTitle("T"),
            recipient_name=BoxRecipientName("R"),
            status=BoxStatus.ACTIVE,
        )

        assert box.id is not None
        assert box.created_at.tzinfo is not None
        assert box.updated_at.tzinfo is not None


class TestBoxAggregateItems:
    def test_add_item_assigns_sort_order_and_box_id(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        media_file_id = uuid.uuid4()
        before = box.updated_at

        item = box.add_item(
            media_file_id=media_file_id,
            item_type=BoxItemType.IMAGE,
            caption=BoxItemCaption("Hi"),
        )

        assert len(box.items) == 1
        assert item.box_id == box.id
        assert item.media_file_id == media_file_id
        assert item.sort_order.value == 1
        assert item.caption is not None
        assert item.caption.value == "Hi"
        assert box.updated_at >= before

    def test_add_item_rejects_duplicate_sort_order(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.IMAGE,
            sort_order=SortOrder(1),
        )

        with pytest.raises(BoxItemDuplicateSortOrderError):
            box.add_item(
                media_file_id=uuid.uuid4(),
                item_type=BoxItemType.GIF,
                sort_order=SortOrder(1),
            )

    def test_remove_item_reindexes_sort_orders(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        first = box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.IMAGE,
        )
        second = box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.VIDEO,
        )
        third = box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.VOICE,
        )

        box.remove_item(first.id)

        assert [item.id for item in box.items] == [second.id, third.id]
        assert [item.sort_order.value for item in box.items] == [1, 2]

    def test_remove_unknown_item_raises(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)

        with pytest.raises(BoxItemNotFoundError):
            box.remove_item(uuid.uuid4())

    def test_reorder_items(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        first = box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.IMAGE,
        )
        second = box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.GIF,
        )
        third = box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.VIDEO,
        )

        box.reorder_items([third.id, first.id, second.id])

        assert [item.id for item in box.items] == [third.id, first.id, second.id]
        assert [item.sort_order.value for item in box.items] == [1, 2, 3]

    def test_reorder_invalid_set_raises(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        item = box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.IMAGE,
        )

        with pytest.raises(BoxItemReorderError):
            box.reorder_items([item.id, uuid.uuid4()])

    def test_update_details(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        new_design_id = uuid.uuid4()
        before = box.updated_at

        box.update_details(
            design_id=new_design_id,
            title=BoxTitle("New title"),
            recipient_name=BoxRecipientName("Лена"),
            activates_at=activates_at,
            timezone="Europe/Moscow",
            message=BoxMessage("Updated"),
            preview_title=BoxPreviewTitle("Preview"),
            preview_image_url=Url("https://example.com/p.png"),
        )

        assert box.design_id == new_design_id
        assert box.title.value == "New title"
        assert box.recipient_name.value == "Лена"
        assert box.timezone == "Europe/Moscow"
        assert box.message is not None
        assert box.message.value == "Updated"
        assert box.updated_at >= before

    def test_update_item_caption(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        item = box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.IMAGE,
        )

        updated = box.update_item(
            item.id,
            caption=BoxItemCaption("New caption"),
            metadata={"poster": "x"},
        )

        assert updated.caption is not None
        assert updated.caption.value == "New caption"
        assert updated.metadata == {"poster": "x"}
