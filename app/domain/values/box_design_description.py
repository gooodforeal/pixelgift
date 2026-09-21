from dataclasses import dataclass

from app.domain.exceptions.box_designs import (
    BoxDesignDescriptionEmptyError,
    BoxDesignDescriptionSurroundingWhitespaceError,
    BoxDesignDescriptionTooLongError,
)
from app.domain.values.base import BaseValueObject

MAX_LENGTH = 40


@dataclass(frozen=True)
class BoxDesignDescription(BaseValueObject[str]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        description = value.strip()

        if not description:
            raise BoxDesignDescriptionEmptyError(value)

        if description != value:
            raise BoxDesignDescriptionSurroundingWhitespaceError(value)

        if len(description) > MAX_LENGTH:
            raise BoxDesignDescriptionTooLongError(value)
