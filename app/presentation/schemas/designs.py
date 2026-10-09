"""Схемы дизайнов боксов и оценок."""

from typing import Any
import uuid

from pydantic import BaseModel, Field

from app.presentation.schemas.base import BaseResponseSchema


class GiftBoxPaletteConfig(BaseModel):
    """Цвета 3D-подарка в theme_config."""
    body: str | None = None
    bodyDark: str | None = None
    lid: str | None = None
    lidLight: str | None = None
    ribbon: str | None = None
    ribbonDark: str | None = None


class ThemeConfigSchema(BaseModel):
    """Визуальные параметры темы дизайна."""
    gradient: list[str] | None = None
    accent: str | None = None
    text: str | None = None
    particle: str | None = None
    cover_object_position: str | None = None
    background_image_url: str | None = None
    preview_image_url_light: str | None = None
    gift_box: GiftBoxPaletteConfig | None = None


class BoxDesignSchema(BaseModel):
    """Дизайн бокса для каталога."""
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
    """Ответ с одним дизайном."""
    pass


class BoxDesignListResponse(BaseResponseSchema[list[BoxDesignSchema]]):
    """Ответ со списком дизайнов."""
    pass


class AdminBoxDesignSchema(BoxDesignSchema):
    """Дизайн с админ-полями."""
    is_active: bool
    preview_asset_id: uuid.UUID | None = None
    preview_asset_id_light: uuid.UUID | None = None


class AdminBoxDesignResponse(BaseResponseSchema[AdminBoxDesignSchema]):
    """Ответ админ-API с одним дизайном."""
    pass


class AdminBoxDesignListResponse(BaseResponseSchema[list[AdminBoxDesignSchema]]):
    """Ответ админ-API со списком дизайнов."""
    pass


class RateDesignRequest(BaseModel):
    """Тело PUT оценки дизайна."""
    stars: int = Field(..., ge=1, le=5)


class DesignRatingSchema(BaseModel):
    """Агрегированная оценка после голосования."""
    design_id: uuid.UUID
    stars: int
    rating_avg: float
    rating_count: int


class DesignRatingResponse(BaseResponseSchema[DesignRatingSchema]):
    """Ответ PUT /designs/{id}/rating."""
    pass


class CreateBoxDesignRequest(BaseModel):
    """Тело создания дизайна."""
    code: str
    name: str
    preview_image_url: str
    description: str | None = None
    theme_config: ThemeConfigSchema | dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    sort_order: int = 1


class UpdateBoxDesignRequest(BaseModel):
    """Тело полного обновления дизайна."""
    code: str
    name: str
    preview_image_url: str
    description: str | None = None
    theme_config: ThemeConfigSchema | dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    sort_order: int = 1


class PatchBoxDesignRequest(BaseModel):
    """Тело частичного обновления дизайна."""
    code: str | None = None
    name: str | None = None
    preview_image_url: str | None = None
    description: str | None = None
    theme_config: ThemeConfigSchema | dict[str, Any] | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class DesignAssetUploadSchema(BaseModel):
    """Загруженный ассет дизайна."""
    id: uuid.UUID
    url: str
    mime_type: str
    size_bytes: int


class DesignAssetUploadResponse(BaseResponseSchema[DesignAssetUploadSchema]):
    """Ответ POST /admin/designs/upload."""
    pass
