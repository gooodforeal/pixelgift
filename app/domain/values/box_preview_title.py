from dataclasses import dataclass

from app.domain.exceptions.boxes import (
    BoxPreviewTitleEmptyError,
    BoxPreviewTitleSurroundingWhitespaceError,
    BoxPreviewTitleTooLongError,
)
from app.domain.values.base import BaseValueObject

MAX_LENGTH = 30


@dataclass(frozen=True)
class BoxPreviewTitle(BaseValueObject[str]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        title = value.strip()

        if not title:
            raise BoxPreviewTitleEmptyError(value)

        if title != value:
            raise BoxPreviewTitleSurroundingWhitespaceError(value)

        if len(title) > MAX_LENGTH:
            raise BoxPreviewTitleTooLongError(value)
