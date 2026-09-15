import uuid
from datetime import datetime, timezone

import pytest

from src.domain.entities.box_items import BoxItemType
from src.domain.aggregates.boxes import MAX_BOX_ITEMS, Box, BoxStatus
from src.domain.exceptions.box_items import BoxItemInvalidError
from src.domain.exceptions.boxes import (
    BoxAlreadyArchivedError,
    BoxAlreadyOpenedError,
    BoxItemDuplicateSortOrderError,
    BoxItemNotFoundError,
    BoxItemReorderError,
    BoxItemsLimitExceededError,
    BoxNotArchivedError,
)
from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_item_caption import BoxItemCaption
from src.domain.values.box_message import BoxMessage
from src.domain.values.box_preview_title import BoxPreviewTitle
from src.domain.values.box_recipient_email import BoxRecipientEmail
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

    def test_add_text_item_without_media(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)

        item = box.add_item(
            item_type=BoxItemType.TEXT,
            caption=BoxItemCaption("Письмо"),
        )

        assert item.media_file_id is None
        assert item.item_type == BoxItemType.TEXT
        assert item.caption is not None
        assert item.caption.value == "Письмо"

    def test_add_drawing_item_with_media(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        media_file_id = uuid.uuid4()

        item = box.add_item(
            media_file_id=media_file_id,
            item_type=BoxItemType.DRAWING,
            caption=BoxItemCaption("Нарисовал сам"),
        )

        assert item.media_file_id == media_file_id
        assert item.item_type == BoxItemType.DRAWING
        assert item.caption is not None
        assert item.caption.value == "Нарисовал сам"

    def test_add_circle_item_with_media(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        media_file_id = uuid.uuid4()

        item = box.add_item(
            media_file_id=media_file_id,
            item_type=BoxItemType.CIRCLE,
            caption=BoxItemCaption("Кружок"),
        )

        assert item.media_file_id == media_file_id
        assert item.item_type == BoxItemType.CIRCLE
        assert item.caption is not None
        assert item.caption.value == "Кружок"

    def test_add_circle_item_requires_media(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)

        with pytest.raises(BoxItemInvalidError):
            box.add_item(item_type=BoxItemType.CIRCLE)

    def test_add_toy_item_with_code(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)

        item = box.add_item(
            item_type=BoxItemType.TOY,
            caption=BoxItemCaption("Для тебя"),
            metadata={"toy_code": "bear"},
        )

        assert item.media_file_id is None
        assert item.item_type == BoxItemType.TOY
        assert item.metadata["toy_code"] == "bear"

    def test_add_toy_item_rejects_invalid_code(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)

        with pytest.raises(BoxItemInvalidError):
            box.add_item(
                item_type=BoxItemType.TOY,
                metadata={"toy_code": "dragon"},
            )

    def test_add_geopoint_item_with_coords(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)

        item = box.add_item(
            item_type=BoxItemType.GEOPOINT,
            caption=BoxItemCaption("Наше место"),
            metadata={"lat": 55.7558, "lng": 37.6173},
        )

        assert item.media_file_id is None
        assert item.item_type == BoxItemType.GEOPOINT
        assert item.metadata["lat"] == 55.7558
        assert item.metadata["lng"] == 37.6173
        assert item.caption is not None
        assert item.caption.value == "Наше место"

    def test_add_geopoint_item_rejects_missing_coords(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)

        with pytest.raises(BoxItemInvalidError):
            box.add_item(
                item_type=BoxItemType.GEOPOINT,
                metadata={"lat": 55.7558},
            )

    def test_add_geopoint_item_rejects_out_of_range(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)

        with pytest.raises(BoxItemInvalidError):
            box.add_item(
                item_type=BoxItemType.GEOPOINT,
                metadata={"lat": 99.0, "lng": 37.0},
            )

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

    def test_add_item_rejects_more_than_max_items(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        for _ in range(MAX_BOX_ITEMS):
            box.add_item(
                media_file_id=uuid.uuid4(),
                item_type=BoxItemType.IMAGE,
            )

        with pytest.raises(BoxItemsLimitExceededError):
            box.add_item(
                media_file_id=uuid.uuid4(),
                item_type=BoxItemType.IMAGE,
            )

        assert len(box.items) == MAX_BOX_ITEMS

    def test_add_item_allowed_again_after_remove(self, activates_at: ActivatesAt):
        box = _make_box(activates_at)
        for _ in range(MAX_BOX_ITEMS):
            box.add_item(
                media_file_id=uuid.uuid4(),
                item_type=BoxItemType.IMAGE,
            )

        box.remove_item(box.items[0].id)
        box.add_item(media_file_id=uuid.uuid4(), item_type=BoxItemType.IMAGE)

        assert len(box.items) == MAX_BOX_ITEMS

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
            recipient_email=BoxRecipientEmail("lena@example.com"),
        )

        assert box.design_id == new_design_id
        assert box.title.value == "New title"
        assert box.recipient_name.value == "Лена"
        assert box.recipient_email is not None
        assert box.recipient_email.value == "lena@example.com"
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


class TestBoxArchiveUnarchive:
    def test_unarchive_draft_restores_draft(self, activates_at: ActivatesAt):
        box = _make_box(activates_at, status=BoxStatus.DRAFT)
        box.archive()
        assert box.status == BoxStatus.ARCHIVED

        box.unarchive()

        assert box.status == BoxStatus.DRAFT

    def test_unarchive_published_restores_scheduled(self, activates_at: ActivatesAt):
        box = _make_box(activates_at, status=BoxStatus.DRAFT)
        box.add_item(media_file_id=uuid.uuid4(), item_type=BoxItemType.IMAGE)
        box.publish()
        box.archive()

        box.unarchive()

        assert box.status == BoxStatus.SCHEDULED
        assert box.published_at is not None

    def test_unarchive_published_past_date_restores_active(
        self, activates_at: ActivatesAt
    ):
        past = ActivatesAt.reconstitute(datetime(2020, 1, 1, tzinfo=timezone.utc))
        box = _make_box(past, status=BoxStatus.DRAFT)
        box.add_item(media_file_id=uuid.uuid4(), item_type=BoxItemType.IMAGE)
        box.publish()
        box.archive()

        box.unarchive()

        assert box.status == BoxStatus.ACTIVE

    def test_activate_if_due_promotes_scheduled(self):
        past = ActivatesAt.reconstitute(datetime(2020, 1, 1, tzinfo=timezone.utc))
        box = _make_box(past, status=BoxStatus.SCHEDULED)

        assert box.activate_if_due() is True
        assert box.status == BoxStatus.ACTIVE

    def test_activate_if_due_skips_future(self, activates_at: ActivatesAt):
        box = _make_box(activates_at, status=BoxStatus.SCHEDULED)

        assert box.activate_if_due() is False
        assert box.status == BoxStatus.SCHEDULED

    def test_mark_opened_from_scheduled(self):
        past = ActivatesAt.reconstitute(datetime(2020, 1, 1, tzinfo=timezone.utc))
        box = _make_box(past, status=BoxStatus.SCHEDULED)

        assert box.mark_opened() is True
        assert box.status == BoxStatus.OPENED
        assert box.first_opened_at is not None

    def test_mark_opened_from_active(self):
        past = ActivatesAt.reconstitute(datetime(2020, 1, 1, tzinfo=timezone.utc))
        box = _make_box(past, status=BoxStatus.ACTIVE)

        assert box.mark_opened() is True
        assert box.status == BoxStatus.OPENED

    def test_unarchive_rejects_opened_box(self, activates_at: ActivatesAt):
        box = _make_box(
            activates_at,
            status=BoxStatus.ARCHIVED,
            first_opened_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
            published_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        )

        with pytest.raises(BoxAlreadyOpenedError):
            box.unarchive()

    def test_unarchive_rejects_non_archived(self, activates_at: ActivatesAt):
        box = _make_box(activates_at, status=BoxStatus.DRAFT)

        with pytest.raises(BoxNotArchivedError):
            box.unarchive()
