from src.domain.exceptions.base import BaseException


class BoxDesignNameError(BaseException):
    """Базовая ошибка валидации названия дизайна."""


class BoxDesignNameSurroundingWhitespaceError(BoxDesignNameError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design name must not have surrounding whitespace")


class BoxDesignNameEmptyError(BoxDesignNameError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design name must not be empty")


class BoxDesignNameTooLongError(BoxDesignNameError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design name is too long")


class BoxDesignDescriptionError(BaseException):
    """Базовая ошибка валидации описания дизайна."""


class BoxDesignDescriptionSurroundingWhitespaceError(BoxDesignDescriptionError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design description must not have surrounding whitespace")


class BoxDesignDescriptionEmptyError(BoxDesignDescriptionError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design description must not be empty")


class BoxDesignDescriptionTooLongError(BoxDesignDescriptionError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design description is too long")
