"""Ошибки подписи элемента бокса и инвариантов типа элемента."""

from app.domain.exceptions.base import BaseException


class BoxItemCaptionError(BaseException):
    """Базовая ошибка валидации подписи к элементу бокса."""


class BoxItemCaptionSurroundingWhitespaceError(BoxItemCaptionError):
    """Подпись элемента содержит пробелы по краям."""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box item caption must not have surrounding whitespace")


class BoxItemCaptionEmptyError(BoxItemCaptionError):
    """Подпись элемента пустая."""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box item caption must not be empty")


class BoxItemCaptionTooLongError(BoxItemCaptionError):
    """Подпись элемента слишком длинная."""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box item caption is too long")


class BoxItemInvalidError(BaseException):
    """Несоответствие payload элемента его типу или лимитам агрегата."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
