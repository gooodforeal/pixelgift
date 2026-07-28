from dataclasses import dataclass

from src.domain.exceptions.sort_order import (
    SortOrderNonPositiveError,
    SortOrderNotIntegerError,
)
from src.domain.values.base import BaseValueObject


@dataclass(frozen=True)
class SortOrder(BaseValueObject[int]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise SortOrderNotIntegerError(value)
        if value <= 0:
            raise SortOrderNonPositiveError(value)
