from datetime import datetime
from typing import Any, Literal, Self
import uuid

from pydantic import BaseModel, EmailStr, Field, model_validator


class BoxItemResponse(BaseModel):
    id: uuid.UUID
    media_file_id: uuid.UUID | None = None
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
    recipient_email: EmailStr | None = None
    unlock_password: str | None = None
    activates_at: datetime
    status: str
    timezone: str = "UTC"
    message: str | None = None
    preview_title: str | None = None
    preview_image_url: str | None = None
    published_at: datetime | None = None
    first_opened_at: datetime | None = None
    items: list[BoxItemResponse] = Field(default_factory=list)


class PaginatedBoxesResponse(BaseModel):
    items: list[BoxResponse]
    total: int
    page: int
    page_size: int
    status_counts: dict[str, int] = Field(default_factory=dict)


class CreateBoxRequest(BaseModel):
    design_id: uuid.UUID
    title: str = Field(max_length=30)
    recipient_name: str = Field(max_length=30)
    recipient_email: EmailStr
    unlock_password: str = Field(min_length=4, max_length=12, pattern=r"^[A-Za-z0-9]+$")
    activates_at: datetime
    timezone: str = "UTC"
    public_slug: str | None = None
    message: str | None = Field(default=None, max_length=300)
    preview_title: str | None = Field(default=None, max_length=30)
    preview_image_url: str | None = None


class UpdateBoxRequest(BaseModel):
    design_id: uuid.UUID
    title: str = Field(max_length=30)
    recipient_name: str = Field(max_length=30)
    recipient_email: EmailStr
    unlock_password: str = Field(min_length=4, max_length=12, pattern=r"^[A-Za-z0-9]+$")
    activates_at: datetime
    timezone: str = "UTC"
    message: str | None = Field(default=None, max_length=300)
    preview_title: str | None = Field(default=None, max_length=30)
    preview_image_url: str | None = None


class AddBoxItemRequest(BaseModel):
    media_file_id: uuid.UUID | None = None
    item_type: (
        Literal["text", "toy", "geopoint", "question", "drawing", "circle"] | None
    ) = None
    caption: str | None = Field(default=None, max_length=300)
    sort_order: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_item_mode(self) -> Self:
        if self.item_type == "text":
            if self.media_file_id is not None:
                raise ValueError("Text item must not include media_file_id")
            if not self.caption or not self.caption.strip():
                raise ValueError("Text item requires non-empty caption")
        elif self.item_type == "toy":
            if self.media_file_id is not None:
                raise ValueError("Toy item must not include media_file_id")
            toy_code = self.metadata.get("toy_code")
            if not isinstance(toy_code, str) or not toy_code.strip():
                raise ValueError("Toy item requires metadata.toy_code")
        elif self.item_type == "geopoint":
            if self.media_file_id is not None:
                raise ValueError("Geopoint item must not include media_file_id")
            lat = self.metadata.get("lat")
            lng = self.metadata.get("lng")
            if not isinstance(lat, (int, float)) or isinstance(lat, bool):
                raise ValueError("Geopoint item requires numeric metadata.lat")
            if not isinstance(lng, (int, float)) or isinstance(lng, bool):
                raise ValueError("Geopoint item requires numeric metadata.lng")
            if not (-90 <= float(lat) <= 90):
                raise ValueError("metadata.lat must be between -90 and 90")
            if not (-180 <= float(lng) <= 180):
                raise ValueError("metadata.lng must be between -180 and 180")
        elif self.item_type == "question":
            if self.media_file_id is not None:
                raise ValueError("Question item must not include media_file_id")
            from app.domain.helpers.box_items import parse_question_metadata

            try:
                self.metadata = parse_question_metadata(self.metadata)
            except ValueError as exc:
                raise ValueError(str(exc)) from exc
        elif self.item_type == "drawing":
            if self.media_file_id is None:
                raise ValueError("Drawing item requires media_file_id")
        elif self.item_type == "circle":
            if self.media_file_id is None:
                raise ValueError("Circle item requires media_file_id")
        elif self.media_file_id is None:
            raise ValueError("media_file_id is required for media items")
        return self


class UpdateBoxItemRequest(BaseModel):
    caption: str | None = Field(default=None, max_length=300)
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
    password_required: bool = False
    message: str | None = None
    design_code: str | None = None
    theme_config: dict[str, Any] = Field(default_factory=dict)
    items: list[BoxItemResponse] = Field(default_factory=list)


class UnlockPublicBoxRequest(BaseModel):
    password: str = Field(min_length=1, max_length=12)


class UnlockPublicBoxResponse(BaseModel):
    unlock_token: str | None = None
    box: PublicBoxResponse
