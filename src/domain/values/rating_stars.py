from dataclasses import dataclass

from src.domain.exceptions.design_ratings import (
    DesignRatingStarsNotIntegerError,
    DesignRatingStarsOutOfRangeError,
)
from src.domain.values.base import BaseValueObject


@dataclass(frozen=True)
class RatingStars(BaseValueObject[int]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise DesignRatingStarsNotIntegerError(value)
        if value < 1 or value > 5:
            raise DesignRatingStarsOutOfRangeError(value)
