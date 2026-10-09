"""Идентификатор пользователя Telegram как строка цифр."""

from dataclasses import dataclass

from app.domain.exceptions.users import (
    TelegramIdNonPositiveError,
    TelegramIdNotNumericError,
    TelegramIdTooLongError,
)
from app.domain.values.base import BaseValueObject


@dataclass(frozen=True)
class TelegramId(BaseValueObject[str]):
    """Положительное число длиной не более 20 символов."""
    def __post_init__(self):
        self.validate(self.value)

    def validate(self, value: str) -> None:
        try:
            numeric = int(value)
        except (TypeError, ValueError):
            raise TelegramIdNotNumericError(value)

        if numeric <= 0:
            raise TelegramIdNonPositiveError(value)

        if len(value) > 20:
            raise TelegramIdTooLongError(value)
