"""Оценка дизайна звёздами от 1 до 5."""

from dataclasses import dataclass

from app.domain.exceptions.design_ratings import (
    DesignRatingStarsNotIntegerError,
    DesignRatingStarsOutOfRangeError,
)
from app.domain.values.base import BaseValueObject


@dataclass(frozen=True)
class RatingStars(BaseValueObject[int]):
    """Целое число звёзд; bool не допускается."""
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise DesignRatingStarsNotIntegerError(value)
        if value < 1 or value > 5:
            raise DesignRatingStarsOutOfRangeError(value)
