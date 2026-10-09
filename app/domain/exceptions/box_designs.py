"""Ошибки каталога дизайнов и ассетов."""

import uuid

from app.domain.exceptions.base import BaseException


class BoxDesignNotFoundError(BaseException):
    """Дизайн бокса не найден."""
    status_code = 404

    def __init__(self, design_id: uuid.UUID) -> None:
        self.design_id = design_id
        super().__init__(f"Box design not found: {design_id}")


class BoxDesignCodeConflictError(BaseException):
    """Код дизайна уже занят."""
    status_code = 409

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Box design code already exists: {code}")


class DesignAssetNotFoundError(BaseException):
    """Ассет дизайна не найден."""
    status_code = 404

    def __init__(self, asset_id: uuid.UUID) -> None:
        self.asset_id = asset_id
        super().__init__(f"Design asset not found: {asset_id}")


class BoxDesignNameError(BaseException):
    """Базовая ошибка валидации названия дизайна."""


class BoxDesignNameSurroundingWhitespaceError(BoxDesignNameError):
    """Имя дизайна содержит пробелы по краям."""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design name must not have surrounding whitespace")


class BoxDesignNameEmptyError(BoxDesignNameError):
    """Имя дизайна пустое."""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design name must not be empty")


class BoxDesignNameTooLongError(BoxDesignNameError):
    """Имя дизайна слишком длинное."""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design name is too long")


class BoxDesignDescriptionError(BaseException):
    """Базовая ошибка валидации описания дизайна."""


class BoxDesignDescriptionSurroundingWhitespaceError(BoxDesignDescriptionError):
    """Описание дизайна содержит пробелы по краям."""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design description must not have surrounding whitespace")


class BoxDesignDescriptionEmptyError(BoxDesignDescriptionError):
    """Описание дизайна пустое."""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design description must not be empty")


class BoxDesignDescriptionTooLongError(BoxDesignDescriptionError):
    """Описание дизайна слишком длинное."""
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box design description is too long")
