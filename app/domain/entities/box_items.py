"""Элемент содержимого подарочного бокса и допустимые типы."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.values.box_item_caption import BoxItemCaption
from app.domain.values.sort_order import SortOrder


class BoxItemType(StrEnum):
    """Тип медиа или интерактивного блока внутри бокса."""

    IMAGE = "image"
    DRAWING = "drawing"
    GIF = "gif"
    VIDEO = "video"
    CIRCLE = "circle"
    VOICE = "voice"
    TEXT = "text"
    TOY = "toy"
    GEOPOINT = "geopoint"
    QUESTION = "question"


QUESTION_TEXT_MIN = 3
QUESTION_TEXT_MAX = 50
QUESTION_OPTIONS_MIN = 2
QUESTION_OPTIONS_MAX = 4
QUESTION_OPTION_MAX = 40


TOY_CODES: frozenset[str] = frozenset(
    {"bear", "bunny", "fox", "kitty", "penguin", "dino"}
)


@dataclass(frozen=False, kw_only=True)
class BoxItem(BaseEntity):
    """Один слот содержимого бокса с порядком, подписью и metadata."""

    box_id: uuid.UUID
    media_file_id: uuid.UUID | None
    item_type: BoxItemType
    sort_order: SortOrder
    caption: BoxItemCaption | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
