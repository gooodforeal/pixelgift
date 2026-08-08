from dataclasses import dataclass
import uuid

from src.domain.entities.base import BaseEntity
from src.domain.values.rating_stars import RatingStars


@dataclass(frozen=False, kw_only=True)
class DesignRating(BaseEntity):
    user_id: uuid.UUID
    design_id: uuid.UUID
    stars: RatingStars
