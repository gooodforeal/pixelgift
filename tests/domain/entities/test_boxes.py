import uuid
from datetime import datetime, timezone

from src.domain.entities.boxes import Box, BoxStatus
from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_message import BoxMessage
from src.domain.values.box_preview_title import BoxPreviewTitle
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle
from src.domain.values.public_slug import PublicSlug
from src.domain.values.url import Url


class TestBox:
    def test_create_minimal(self, activates_at: ActivatesAt):
        owner_id = uuid.uuid4()
        design_id = uuid.uuid4()

        box = Box(
            owner_id=owner_id,
            design_id=design_id,
            public_slug=PublicSlug("gift-42"),
            title=BoxTitle("Happy birthday"),
            recipient_name=BoxRecipientName("Маша"),
            activates_at=activates_at,
            status=BoxStatus.DRAFT,
        )

        assert box.owner_id == owner_id
        assert box.design_id == design_id
        assert box.public_slug.value == "gift-42"
        assert box.status == BoxStatus.DRAFT
        assert box.timezone == "UTC"
        assert box.message is None
        assert box.preview_title is None

    def test_create_with_optional_fields(self, activates_at: ActivatesAt):
        published = datetime(2026, 6, 1, tzinfo=timezone.utc)
        opened = datetime(2026, 6, 2, tzinfo=timezone.utc)

        box = Box(
            owner_id=uuid.uuid4(),
            design_id=uuid.uuid4(),
            public_slug=PublicSlug("summer"),
            title=BoxTitle("For you"),
            recipient_name=BoxRecipientName("Kate"),
            activates_at=activates_at,
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
        box = Box(
            owner_id=uuid.uuid4(),
            design_id=uuid.uuid4(),
            public_slug=PublicSlug("a"),
            title=BoxTitle("T"),
            recipient_name=BoxRecipientName("R"),
            activates_at=activates_at,
            status=BoxStatus.ACTIVE,
        )

        assert box.id is not None
        assert box.created_at.tzinfo is not None
        assert box.updated_at.tzinfo is not None
