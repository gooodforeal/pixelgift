from dataclasses import dataclass

from src.domain.values.base import BaseValueObject
from src.domain.exceptions.users import TelegramIdInvalidError


@dataclass(frozen=True)
class TelegramId(BaseValueObject[str]):

    def __post_init__(self):
        self.validate(self.value)

    def validate(self, value: str) -> None:
        try:
            int(value)
        except Exception:
            raise TelegramIdInvalidError(value)

        if int(value) <= 0:
            raise TelegramIdInvalidError(value)

        if len(value) > 20:
            raise TelegramIdInvalidError(value)

        