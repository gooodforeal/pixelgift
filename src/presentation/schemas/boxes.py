from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, Field


class BoxItemResponse(BaseModel):
    id: uuid.UUID
    media_file_id: uuid.UUID
    item_type: str
    sort_order: int
    caption: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BoxResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    design_id: uuid.UUID
    public_slug: str
    title: str
    recipient_name: str
    activates_at: datetime
    status: str
    timezone: str = "UTC"
    message: str | None = None
    preview_title: str | None = None
    preview_image_url: str | None = None
    published_at: datetime | None = None
    first_opened_at: datetime | None = None
    items: list[BoxItemResponse] = Field(default_factory=list)


class CreateBoxRequest(BaseModel):
    design_id: uuid.UUID
    title: str
    recipient_name: str
    activates_at: datetime
    timezone: str = "UTC"
    public_slug: str | None = None
    message: str | None = None
    preview_title: str | None = None
    preview_image_url: str | None = None


class UpdateBoxRequest(BaseModel):
    design_id: uuid.UUID
    title: str
    recipient_name: str
    activates_at: datetime
    timezone: str = "UTC"
    message: str | None = None
    preview_title: str | None = None
    preview_image_url: str | None = None


class AddBoxItemRequest(BaseModel):
    media_file_id: uuid.UUID
    caption: str | None = None
    sort_order: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateBoxItemRequest(BaseModel):
    caption: str | None = None
    metadata: dict[str, Any] | None = None


class ReorderBoxItemsRequest(BaseModel):
    item_ids: list[uuid.UUID]


class MediaFileResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    storage_key: str
    mime_type: str
    media_kind: str
    size_bytes: int
    original_filename: str | None = None


class PublicBoxResponse(BaseModel):
    public_slug: str
    title: str
    recipient_name: str
    activates_at: datetime
    status: str
    timezone: str
    preview_title: str | None = None
    preview_image_url: str | None = None
    content_unlocked: bool
    message: str | None = None
    items: list[BoxItemResponse] = Field(default_factory=list)
