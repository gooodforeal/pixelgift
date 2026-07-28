from dataclasses import dataclass, field
from typing import Any
import uuid

from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_item_caption import BoxItemCaption
from src.domain.values.box_message import BoxMessage
from src.domain.values.box_preview_title import BoxPreviewTitle
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle
from src.domain.values.public_slug import PublicSlug
from src.domain.values.sort_order import SortOrder
from src.domain.values.url import Url


@dataclass(frozen=True, kw_only=True)
class CreateBoxCommand:
    owner_id: uuid.UUID
    design_id: uuid.UUID
    title: BoxTitle
    recipient_name: BoxRecipientName
    activates_at: ActivatesAt
    timezone: str = "UTC"
    public_slug: PublicSlug | None = None
    message: BoxMessage | None = None
    preview_title: BoxPreviewTitle | None = None
    preview_image_url: Url | None = None


@dataclass(frozen=True, kw_only=True)
class UpdateBoxCommand:
    box_id: uuid.UUID
    actor_id: uuid.UUID
    design_id: uuid.UUID
    title: BoxTitle
    recipient_name: BoxRecipientName
    activates_at: ActivatesAt
    timezone: str = "UTC"
    message: BoxMessage | None = None
    preview_title: BoxPreviewTitle | None = None
    preview_image_url: Url | None = None


@dataclass(frozen=True, kw_only=True)
class AddBoxItemCommand:
    box_id: uuid.UUID
    actor_id: uuid.UUID
    media_file_id: uuid.UUID
    caption: BoxItemCaption | None = None
    sort_order: SortOrder | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class UpdateBoxItemCommand:
    box_id: uuid.UUID
    actor_id: uuid.UUID
    item_id: uuid.UUID
    caption: BoxItemCaption | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True, kw_only=True)
class RemoveBoxItemCommand:
    box_id: uuid.UUID
    actor_id: uuid.UUID
    item_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ReorderBoxItemsCommand:
    box_id: uuid.UUID
    actor_id: uuid.UUID
    item_ids: tuple[uuid.UUID, ...]
