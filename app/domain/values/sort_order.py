"""Положительный порядковый номер элемента в списке."""

from dataclasses import dataclass

from app.domain.exceptions.sort_order import (
    SortOrderNonPositiveError,
    SortOrderNotIntegerError,
)
from app.domain.values.base import BaseValueObject


@dataclass(frozen=True)
class SortOrder(BaseValueObject[int]):
    """Целое число > 0 для сортировки элементов или дизайнов."""
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise SortOrderNotIntegerError(value)
        if value <= 0:
            raise SortOrderNonPositiveError(value)
