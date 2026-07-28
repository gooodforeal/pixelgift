import uuid
from datetime import datetime, timedelta, timezone

from src.domain.aggregates.boxes import Box, BoxStatus
from src.domain.entities.box_items import BoxItemType
from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_item_caption import BoxItemCaption
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle
from src.domain.values.public_slug import PublicSlug
from src.infrastructure.mappers.boxes import box_to_entity, box_to_model


class TestBoxMapper:
    def test_roundtrip_with_items_and_past_activates_at(self):
        activates_at = ActivatesAt.reconstitute(
            datetime.now(timezone.utc) - timedelta(days=1)
        )
        box = Box(
            owner_id=uuid.uuid4(),
            design_id=uuid.uuid4(),
            public_slug=PublicSlug("gift-mapper"),
            title=BoxTitle("Title"),
            recipient_name=BoxRecipientName("Маша"),
            activates_at=activates_at,
            status=BoxStatus.ACTIVE,
        )
        box.add_item(
            media_file_id=uuid.uuid4(),
            item_type=BoxItemType.IMAGE,
            caption=BoxItemCaption("Hi"),
        )

        restored = box_to_entity(box_to_model(box))

        assert restored.id == box.id
        assert restored.status == BoxStatus.ACTIVE
        assert restored.activates_at.value == activates_at.value
        assert len(restored.items) == 1
        assert restored.items[0].caption is not None
        assert restored.items[0].caption.value == "Hi"
        assert restored.items[0].item_type == BoxItemType.IMAGE
