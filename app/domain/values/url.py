"""HTTP(S) URL с обязательным хостом."""

from dataclasses import dataclass
from urllib.parse import urlparse

from app.domain.exceptions.url import (
    UrlEmptyError,
    UrlMissingHostError,
    UrlSurroundingWhitespaceError,
    UrlUnsupportedSchemeError,
)
from app.domain.values.base import BaseValueObject

_ALLOWED_SCHEMES = frozenset({"http", "https"})


@dataclass(frozen=True)
class Url(BaseValueObject[str]):
    """Не пустой URL без краевых пробелов; допускаются только http и https."""
    def __post_init__(self) -> None:
        self.validate(self.value)

    def validate(self, value: str) -> None:
        url = value.strip()

        if not url:
            raise UrlEmptyError(value)

        if url != value:
            raise UrlSurroundingWhitespaceError(value)

        parsed = urlparse(url)
        if parsed.scheme not in _ALLOWED_SCHEMES:
            raise UrlUnsupportedSchemeError(value)
        if not parsed.netloc:
            raise UrlMissingHostError(value)
