from dataclasses import dataclass

from src.domain.exceptions.boxes import (
    BoxRecipientNameEmptyError,
    BoxRecipientNameSurroundingWhitespaceError,
    BoxRecipientNameTooLongError,
)
from src.domain.values.base import BaseValueObject

MAX_LENGTH = 40


@dataclass(frozen=True)
class BoxRecipientName(BaseValueObject[str]):
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
