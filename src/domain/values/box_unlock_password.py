import re
from dataclasses import dataclass

from src.domain.exceptions.boxes import (
    BoxUnlockPasswordEmptyError,
    BoxUnlockPasswordFormatError,
    BoxUnlockPasswordTooLongError,
    BoxUnlockPasswordTooShortError,
)
from src.domain.values.base import BaseValueObject

MIN_LENGTH = 4
MAX_LENGTH = 12
_PATTERN = re.compile(r"^[A-Za-z0-9]+$")


@dataclass(frozen=True)
class BoxUnlockPassword(BaseValueObject[str]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        if not value:
            raise BoxUnlockPasswordEmptyError(value)

        if value.strip() != value:
            raise BoxUnlockPasswordFormatError(value)

        if len(value) < MIN_LENGTH:
            raise BoxUnlockPasswordTooShortError(value)

        if len(value) > MAX_LENGTH:
            raise BoxUnlockPasswordTooLongError(value)

        if not _PATTERN.fullmatch(value):
            raise BoxUnlockPasswordFormatError(value)
