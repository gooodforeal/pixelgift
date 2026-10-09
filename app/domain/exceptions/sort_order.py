"""Ошибки value object SortOrder."""

from app.domain.exceptions.base import BaseException


class SortOrderError(BaseException):
    """Базовая ошибка валидации порядка сортировки."""


class SortOrderNotIntegerError(SortOrderError):
    """Sort order должен быть целым числом."""
    def __init__(self, sort_order: int) -> None:
        self.sort_order = sort_order
        super().__init__(f"Sort order must be an integer, got {sort_order!r}")


class SortOrderNonPositiveError(SortOrderError):
    """Sort order должен быть положительным."""
    def __init__(self, sort_order: int) -> None:
        self.sort_order = sort_order
        super().__init__(f"Sort order must be greater than zero, got {sort_order}")
