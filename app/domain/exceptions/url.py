"""Ошибки value object Url."""

from app.domain.exceptions.base import BaseException


class UrlError(BaseException):
    """Базовая ошибка валидации URL."""


class UrlEmptyError(UrlError):
    """URL пустой."""
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__("URL must not be empty")


class UrlSurroundingWhitespaceError(UrlError):
    """URL содержит пробелы по краям."""
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__("URL must not have surrounding whitespace")


class UrlUnsupportedSchemeError(UrlError):
    """Неподдерживаемая схема URL."""
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"URL scheme is not supported: {url!r}")


class UrlMissingHostError(UrlError):
    """В URL отсутствует host."""
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"URL must include a host: {url!r}")
