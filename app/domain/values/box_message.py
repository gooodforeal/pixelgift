from dataclasses import dataclass

from app.domain.exceptions.boxes import (
    BoxMessageEmptyError,
    BoxMessageSurroundingWhitespaceError,
    BoxMessageTooLongError,
)
from app.domain.values.base import BaseValueObject

MAX_LENGTH = 300


@dataclass(frozen=True)
class BoxMessage(BaseValueObject[str]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        message = value.strip()

        if not message:
            raise BoxMessageEmptyError(value)

        if message != value:
            raise BoxMessageSurroundingWhitespaceError(value)

        if len(message) > MAX_LENGTH:
            raise BoxMessageTooLongError(value)
