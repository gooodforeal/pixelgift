import re
from dataclasses import dataclass

from app.domain.exceptions.boxes import (
    PublicSlugFormatError,
    PublicSlugSurroundingWhitespaceError,
)
from app.domain.values.base import BaseValueObject

_SLUG_RE = re.compile(r"^(?:[a-z0-9]|[a-z0-9][a-z0-9_-]{0,30}[a-z0-9])$")


@dataclass(frozen=True)
class PublicSlug(BaseValueObject[str]):
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        slug = value.strip()

        if slug != value:
            raise PublicSlugSurroundingWhitespaceError(value)

        if not _SLUG_RE.fullmatch(slug):
            raise PublicSlugFormatError(value)
