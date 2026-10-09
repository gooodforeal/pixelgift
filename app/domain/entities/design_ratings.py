"""Оценка пользователя дизайна бокса."""

from dataclasses import dataclass
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.values.rating_stars import RatingStars


@dataclass(frozen=False, kw_only=True)
class DesignRating(BaseEntity):
    """Звёзды (1–5), поставленные пользователем конкретному design_id."""

    user_id: uuid.UUID
    design_id: uuid.UUID
    stars: RatingStars
