from typing import Any
import uuid

from pydantic import BaseModel, Field


class GiftBoxPaletteConfig(BaseModel):
    body: str | None = None
    bodyDark: str | None = None
    lid: str | None = None
    lidLight: str | None = None
    ribbon: str | None = None
    ribbonDark: str | None = None


class ThemeConfigSchema(BaseModel):
    gradient: list[str] | None = None
    accent: str | None = None
    text: str | None = None
    particle: str | None = None
    cover_object_position: str | None = None
    background_image_url: str | None = None
    preview_image_url_light: str | None = None
    gift_box: GiftBoxPaletteConfig | None = None


class BoxDesignResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    preview_image_url: str
    sort_order: int
    description: str | None = None
    theme_config: dict[str, Any] = Field(default_factory=dict)
    rating_avg: float = 0.0
    rating_count: int = 0
    my_rating: int | None = None


class AdminBoxDesignResponse(BoxDesignResponse):
    is_active: bool


class RateDesignRequest(BaseModel):
    stars: int = Field(..., ge=1, le=5)


class DesignRatingResponse(BaseModel):
    design_id: uuid.UUID
    stars: int
    rating_avg: float
    rating_count: int


class CreateBoxDesignRequest(BaseModel):
    code: str
    name: str
    preview_image_url: str
    description: str | None = None
    theme_config: ThemeConfigSchema | dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    sort_order: int = 1


class UpdateBoxDesignRequest(BaseModel):
    code: str
    name: str
    preview_image_url: str
    description: str | None = None
    theme_config: ThemeConfigSchema | dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    sort_order: int = 1


class PatchBoxDesignRequest(BaseModel):
    code: str | None = None
    name: str | None = None
    preview_image_url: str | None = None
    description: str | None = None
    theme_config: ThemeConfigSchema | dict[str, Any] | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class DesignAssetUploadResponse(BaseModel):
    id: uuid.UUID
    url: str
    mime_type: str
    size_bytes: int
