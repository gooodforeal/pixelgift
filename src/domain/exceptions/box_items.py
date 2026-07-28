from src.domain.exceptions.base import BaseException


class BoxItemCaptionError(BaseException):
    """Базовая ошибка валидации подписи к элементу бокса."""


class BoxItemCaptionSurroundingWhitespaceError(BoxItemCaptionError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box item caption must not have surrounding whitespace")


class BoxItemCaptionEmptyError(BoxItemCaptionError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box item caption must not be empty")


class BoxItemCaptionTooLongError(BoxItemCaptionError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box item caption is too long")
