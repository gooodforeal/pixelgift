from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
import uuid

from src.domain.entities.base import BaseEntity
from src.domain.values.box_item_caption import BoxItemCaption
from src.domain.values.sort_order import SortOrder


class BoxItemType(StrEnum):
    IMAGE = "image"
    DRAWING = "drawing"
    GIF = "gif"
    VIDEO = "video"
    CIRCLE = "circle"
    VOICE = "voice"
    TEXT = "text"
    TOY = "toy"
    GEOPOINT = "geopoint"


TOY_CODES: frozenset[str] = frozenset(
    {"bear", "bunny", "fox", "kitty", "penguin", "dino"}
)


@dataclass(frozen=False, kw_only=True)
class BoxItem(BaseEntity):
    box_id: uuid.UUID
    media_file_id: uuid.UUID | None
    item_type: BoxItemType
    sort_order: SortOrder
    caption: BoxItemCaption | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
