from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.exceptions.boxes import BoxActivatesAtNotInFutureError
from src.domain.values.base import BaseValueObject


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class ActivatesAt(BaseValueObject[datetime]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: datetime, *, now: datetime | None = None) -> None:
        reference = _to_utc(now or datetime.now(timezone.utc))
        activates = _to_utc(value)
        if activates <= reference:
            raise BoxActivatesAtNotInFutureError(value)
