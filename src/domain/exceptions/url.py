from src.domain.exceptions.base import BaseException


class UrlError(BaseException):
    """Базовая ошибка валидации URL."""


class UrlEmptyError(UrlError):
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__("URL must not be empty")


class UrlSurroundingWhitespaceError(UrlError):
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__("URL must not have surrounding whitespace")


class UrlUnsupportedSchemeError(UrlError):
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"URL scheme is not supported: {url!r}")


class UrlMissingHostError(UrlError):
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"URL must include a host: {url!r}")
