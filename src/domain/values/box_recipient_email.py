from dataclasses import dataclass

from pydantic import EmailStr, TypeAdapter, ValidationError

from src.domain.exceptions.boxes import (
    BoxRecipientEmailInvalidError,
    BoxRecipientEmailSurroundingWhitespaceError,
)
from src.domain.values.base import BaseValueObject

_email_adapter: TypeAdapter[EmailStr] = TypeAdapter(EmailStr)


@dataclass(frozen=True)
class BoxRecipientEmail(BaseValueObject[str]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        if value != value.strip():
            raise BoxRecipientEmailSurroundingWhitespaceError(value)

        try:
            _email_adapter.validate_python(value)
        except ValidationError as exc:
            raise BoxRecipientEmailInvalidError(value) from exc
