from dataclasses import dataclass, field
from typing import Any
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.values.box_design_description import BoxDesignDescription
from app.domain.values.box_design_name import BoxDesignName
from app.domain.values.sort_order import SortOrder
from app.domain.values.url import Url


def _default_sort_order() -> SortOrder:
    return SortOrder(1)


@dataclass(frozen=False, kw_only=True)
class BoxDesign(BaseEntity):
    code: str
    name: BoxDesignName
    preview_image_url: Url
    description: BoxDesignDescription | None = None
    theme_config: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    sort_order: SortOrder = field(default_factory=_default_sort_order)
    preview_asset_id: uuid.UUID | None = None
    preview_asset_id_light: uuid.UUID | None = None
