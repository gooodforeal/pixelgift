"""Имя получателя подарка (до 30 символов)."""

from dataclasses import dataclass

from app.domain.exceptions.boxes import (
    BoxRecipientNameEmptyError,
    BoxRecipientNameSurroundingWhitespaceError,
    BoxRecipientNameTooLongError,
)
from app.domain.values.base import BaseValueObject

MAX_LENGTH = 30


@dataclass(frozen=True)
class BoxRecipientName(BaseValueObject[str]):
    """Не пустое имя без краевых пробелов и с лимитом длины."""
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        name = value.strip()

        if not name:
            raise BoxRecipientNameEmptyError(value)

        if name != value:
            raise BoxRecipientNameSurroundingWhitespaceError(value)

        if len(name) > MAX_LENGTH:
            raise BoxRecipientNameTooLongError(value)
