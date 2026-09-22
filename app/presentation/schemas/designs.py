from typing import Any
import uuid

from pydantic import BaseModel, Field

from app.presentation.schemas.base import BaseResponseSchema


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


class BoxDesignSchema(BaseModel):
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


class BoxDesignResponse(BaseResponseSchema[BoxDesignSchema]):
    pass


class BoxDesignListResponse(BaseResponseSchema[list[BoxDesignSchema]]):
    pass


class AdminBoxDesignSchema(BoxDesignSchema):
    is_active: bool
    preview_asset_id: uuid.UUID | None = None
    preview_asset_id_light: uuid.UUID | None = None


class AdminBoxDesignResponse(BaseResponseSchema[AdminBoxDesignSchema]):
    pass


class AdminBoxDesignListResponse(BaseResponseSchema[list[AdminBoxDesignSchema]]):
    pass


class RateDesignRequest(BaseModel):
    stars: int = Field(..., ge=1, le=5)


class DesignRatingSchema(BaseModel):
    design_id: uuid.UUID
    stars: int
    rating_avg: float
    rating_count: int


class DesignRatingResponse(BaseResponseSchema[DesignRatingSchema]):
    pass


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


class DesignAssetUploadSchema(BaseModel):
    id: uuid.UUID
    url: str
    mime_type: str
    size_bytes: int


class DesignAssetUploadResponse(BaseResponseSchema[DesignAssetUploadSchema]):
    pass
