"""Название дизайна бокса (до 15 символов)."""

from dataclasses import dataclass

from app.domain.exceptions.box_designs import (
    BoxDesignNameEmptyError,
    BoxDesignNameSurroundingWhitespaceError,
    BoxDesignNameTooLongError,
)
from app.domain.values.base import BaseValueObject

MAX_LENGTH = 15


@dataclass(frozen=True)
class BoxDesignName(BaseValueObject[str]):
    """Не пустое имя без краевых пробелов и с лимитом длины."""
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        name = value.strip()

        if not name:
            raise BoxDesignNameEmptyError(value)

        if name != value:
            raise BoxDesignNameSurroundingWhitespaceError(value)

        if len(name) > MAX_LENGTH:
            raise BoxDesignNameTooLongError(value)
