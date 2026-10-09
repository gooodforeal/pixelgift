"""Email получателя подарка (опциональное поле бокса)."""

from dataclasses import dataclass

from pydantic import EmailStr, TypeAdapter, ValidationError

from app.domain.exceptions.boxes import (
    BoxRecipientEmailInvalidError,
    BoxRecipientEmailSurroundingWhitespaceError,
)
from app.domain.values.base import BaseValueObject

_email_adapter: TypeAdapter[EmailStr] = TypeAdapter(EmailStr)


@dataclass(frozen=True)
class BoxRecipientEmail(BaseValueObject[str]):
    """Строка email без пробелов по краям, проверяется через Pydantic EmailStr."""
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        if value != value.strip():
            raise BoxRecipientEmailSurroundingWhitespaceError(value)

        try:
            _email_adapter.validate_python(value)
        except ValidationError as exc:
            raise BoxRecipientEmailInvalidError(value) from exc
