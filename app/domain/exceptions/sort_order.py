from app.domain.exceptions.base import BaseException


class SortOrderError(BaseException):
    """Базовая ошибка валидации порядка сортировки."""


class SortOrderNotIntegerError(SortOrderError):
    def __init__(self, sort_order: int) -> None:
        self.sort_order = sort_order
        super().__init__(f"Sort order must be an integer, got {sort_order!r}")


class SortOrderNonPositiveError(SortOrderError):
    def __init__(self, sort_order: int) -> None:
        self.sort_order = sort_order
        super().__init__(f"Sort order must be greater than zero, got {sort_order}")
