from dataclasses import dataclass

from app.domain.exceptions.box_items import (
    BoxItemCaptionEmptyError,
    BoxItemCaptionSurroundingWhitespaceError,
    BoxItemCaptionTooLongError,
)
from app.domain.values.base import BaseValueObject

MAX_LENGTH = 300


@dataclass(frozen=True)
class BoxItemCaption(BaseValueObject[str]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        caption = value.strip()

        if not caption:
            raise BoxItemCaptionEmptyError(value)

        if caption != value:
            raise BoxItemCaptionSurroundingWhitespaceError(value)

        if len(caption) > MAX_LENGTH:
            raise BoxItemCaptionTooLongError(value)
