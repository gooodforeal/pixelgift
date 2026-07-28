from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import uuid

from src.domain.entities.base import BaseEntity
from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_message import BoxMessage
from src.domain.values.box_preview_title import BoxPreviewTitle
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle
from src.domain.values.public_slug import PublicSlug
from src.domain.values.url import Url


class BoxStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass(frozen=False, kw_only=True)
class Box(BaseEntity):
    owner_id: uuid.UUID
    design_id: uuid.UUID
    public_slug: PublicSlug
    title: BoxTitle
    recipient_name: BoxRecipientName
    activates_at: ActivatesAt
    status: BoxStatus
    timezone: str = "UTC"
    message: BoxMessage | None = None
    preview_title: BoxPreviewTitle | None = None
    preview_image_url: Url | None = None
    published_at: datetime | None = None
    first_opened_at: datetime | None = None
