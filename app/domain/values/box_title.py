from dataclasses import dataclass

from app.domain.exceptions.boxes import (
    BoxTitleEmptyError,
    BoxTitleSurroundingWhitespaceError,
    BoxTitleTooLongError,
)
from app.domain.values.base import BaseValueObject

MAX_LENGTH = 30


@dataclass(frozen=True)
class BoxTitle(BaseValueObject[str]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        title = value.strip()

        if not title:
            raise BoxTitleEmptyError(value)

        if title != value:
            raise BoxTitleSurroundingWhitespaceError(value)

        if len(title) > MAX_LENGTH:
            raise BoxTitleTooLongError(value)
