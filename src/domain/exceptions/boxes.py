from datetime import datetime

from src.domain.exceptions.base import BaseException


class PublicSlugError(BaseException):
    """Базовая ошибка валидации публичного slug."""


class PublicSlugSurroundingWhitespaceError(PublicSlugError):
    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Public slug must not have surrounding whitespace: {slug!r}")


class PublicSlugFormatError(PublicSlugError):
    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Public slug {slug!r} has invalid format")


class BoxTitleError(BaseException):
    """Базовая ошибка валидации заголовка бокса."""


class BoxTitleSurroundingWhitespaceError(BoxTitleError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box title must not have surrounding whitespace")


class BoxTitleEmptyError(BoxTitleError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box title must not be empty")


class BoxTitleTooLongError(BoxTitleError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box title is too long")


class BoxRecipientNameError(BaseException):
    """Базовая ошибка валидации имени получателя."""


class BoxRecipientNameSurroundingWhitespaceError(BoxRecipientNameError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Recipient name must not have surrounding whitespace")


class BoxRecipientNameEmptyError(BoxRecipientNameError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Recipient name must not be empty")


class BoxRecipientNameTooLongError(BoxRecipientNameError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Recipient name is too long")


class BoxPreviewTitleError(BaseException):
    """Базовая ошибка валидации превью-заголовка."""


class BoxPreviewTitleSurroundingWhitespaceError(BoxPreviewTitleError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Preview title must not have surrounding whitespace")


class BoxPreviewTitleEmptyError(BoxPreviewTitleError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Preview title must not be empty")


class BoxPreviewTitleTooLongError(BoxPreviewTitleError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Preview title is too long")


class BoxMessageError(BaseException):
    """Базовая ошибка валидации текста сообщения в боксе."""


class BoxMessageSurroundingWhitespaceError(BoxMessageError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box message must not have surrounding whitespace")


class BoxMessageEmptyError(BoxMessageError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box message must not be empty")


class BoxMessageTooLongError(BoxMessageError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Box message is too long")


class BoxActivatesAtError(BaseException):
    """Базовая ошибка валидации времени активации."""


class BoxActivatesAtNotInFutureError(BoxActivatesAtError):
    def __init__(self, activates_at: datetime) -> None:
        self.activates_at = activates_at
        super().__init__("Box activation time must be in the future")
