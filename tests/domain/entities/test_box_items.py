import uuid

from src.domain.entities.box_items import BoxItem, BoxItemType
from src.domain.values.box_item_caption import BoxItemCaption
from src.domain.values.sort_order import SortOrder


class TestBoxItem:
    def test_create_minimal(self):
        box_id = uuid.uuid4()
        media_file_id = uuid.uuid4()

        item = BoxItem(
            box_id=box_id,
            media_file_id=media_file_id,
            item_type=BoxItemType.IMAGE,
            sort_order=SortOrder(1),
        )

        assert item.box_id == box_id
        assert item.media_file_id == media_file_id
        assert item.item_type == BoxItemType.IMAGE
        assert item.sort_order.value == 1
        assert item.caption is None
        assert item.metadata == {}

    def test_create_with_optional_fields(self):
        item = BoxItem(
            box_id=uuid.uuid4(),
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.VIDEO,
            sort_order=SortOrder(2),
            caption=BoxItemCaption("Our trip"),
            metadata={"poster": "key"},
        )

        assert item.caption is not None
        assert item.caption.value == "Our trip"
        assert item.metadata == {"poster": "key"}

    def test_create_text_item(self):
        item = BoxItem(
            box_id=uuid.uuid4(),
            media_file_id=None,
            item_type=BoxItemType.TEXT,
            sort_order=SortOrder(1),
            caption=BoxItemCaption("Просто текст"),
        )

        assert item.media_file_id is None
        assert item.item_type == BoxItemType.TEXT
        assert item.caption is not None
        assert item.caption.value == "Просто текст"

    def test_create_drawing_item(self):
        media_file_id = uuid.uuid4()

        item = BoxItem(
            box_id=uuid.uuid4(),
            media_file_id=media_file_id,
            item_type=BoxItemType.DRAWING,
            sort_order=SortOrder(3),
        )

        assert item.media_file_id == media_file_id
        assert item.item_type == BoxItemType.DRAWING

    def test_create_circle_item(self):
        media_file_id = uuid.uuid4()

        item = BoxItem(
            box_id=uuid.uuid4(),
            media_file_id=media_file_id,
            item_type=BoxItemType.CIRCLE,
            sort_order=SortOrder(4),
        )

        assert item.media_file_id == media_file_id
        assert item.item_type == BoxItemType.CIRCLE
