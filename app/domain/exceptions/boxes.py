from datetime import datetime
import uuid

from app.domain.exceptions.base import BaseException


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


class BoxRecipientEmailError(BaseException):
    """Базовая ошибка валидации e-mail получателя."""


class BoxRecipientEmailSurroundingWhitespaceError(BoxRecipientEmailError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Recipient email must not have surrounding whitespace")


class BoxRecipientEmailInvalidError(BoxRecipientEmailError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__(f"Recipient email is invalid: {value!r}")


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


class BoxItemAggregateError(BaseException):
    """Базовая ошибка инвариантов элементов внутри агрегата Box."""


class BoxItemDuplicateSortOrderError(BoxItemAggregateError):
    def __init__(self, sort_order: int) -> None:
        self.sort_order = sort_order
        super().__init__(f"Box already has an item with sort_order={sort_order}")


class BoxItemsLimitExceededError(BoxItemAggregateError):
    status_code = 409

    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(f"Box cannot contain more than {limit} items")


class BoxItemNotFoundError(BoxItemAggregateError):
    status_code = 404

    def __init__(self, item_id: uuid.UUID) -> None:
        self.item_id = item_id
        super().__init__(f"Box item not found: {item_id}")


class BoxItemReorderError(BoxItemAggregateError):
    def __init__(self) -> None:
        super().__init__(
            "Reorder must include each existing item id exactly once"
        )


class BoxNotFoundError(BaseException):
    status_code = 404

    def __init__(self, box_id: uuid.UUID) -> None:
        self.box_id = box_id
        super().__init__(f"Box not found: {box_id}")


class BoxNotFoundBySlugError(BaseException):
    status_code = 404

    def __init__(self, public_slug: str) -> None:
        self.public_slug = public_slug
        super().__init__(f"Box not found for slug: {public_slug!r}")


class BoxAccessDeniedError(BaseException):
    status_code = 403

    def __init__(self, box_id: uuid.UUID, actor_id: uuid.UUID) -> None:
        self.box_id = box_id
        self.actor_id = actor_id
        super().__init__(f"Actor {actor_id} cannot modify box {box_id}")


class BoxNotEditableError(BaseException):
    status_code = 409

    def __init__(self, box_id: uuid.UUID, status: str) -> None:
        self.box_id = box_id
        self.status = status
        super().__init__(f"Box {box_id} with status {status!r} cannot be edited")


class PublicSlugAlreadyTakenError(PublicSlugError):
    status_code = 409

    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Public slug already taken: {slug!r}")


class BoxNotPublishableError(BaseException):
    status_code = 409

    def __init__(self, box_id: uuid.UUID, status: str) -> None:
        self.box_id = box_id
        self.status = status
        super().__init__(f"Box {box_id} with status {status!r} cannot be published")


class BoxCertificateNotAvailableError(BaseException):
    status_code = 409

    def __init__(self, box_id: uuid.UUID, status: str) -> None:
        self.box_id = box_id
        self.status = status
        super().__init__(
            f"Certificate for box {box_id} is available only after publish "
            f"(current status {status!r})"
        )


class BoxWithoutItemsError(BaseException):
    def __init__(self, box_id: uuid.UUID) -> None:
        self.box_id = box_id
        super().__init__(f"Box {box_id} has no items and cannot be published")


class BoxAlreadyArchivedError(BaseException):
    status_code = 409

    def __init__(self, box_id: uuid.UUID) -> None:
        self.box_id = box_id
        super().__init__(f"Box {box_id} is already archived")


class BoxNotArchivedError(BaseException):
    status_code = 409

    def __init__(self, box_id: uuid.UUID) -> None:
        self.box_id = box_id
        super().__init__(f"Box {box_id} is not archived")


class BoxAlreadyOpenedError(BaseException):
    status_code = 409

    def __init__(self, box_id: uuid.UUID) -> None:
        self.box_id = box_id
        super().__init__(
            f"Box {box_id} was already opened by the recipient and cannot be unarchived"
        )


class BoxContentLockedError(BaseException):
    status_code = 403

    def __init__(self, public_slug: str) -> None:
        self.public_slug = public_slug
        super().__init__(f"Box content is still locked: {public_slug!r}")


class BoxUnlockPasswordError(BaseException):
    """Базовая ошибка валидации пароля открытия бокса."""


class BoxUnlockPasswordEmptyError(BoxUnlockPasswordError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Unlock password must not be empty")


class BoxUnlockPasswordTooShortError(BoxUnlockPasswordError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Unlock password is too short")


class BoxUnlockPasswordTooLongError(BoxUnlockPasswordError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__("Unlock password is too long")


class BoxUnlockPasswordFormatError(BoxUnlockPasswordError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__(
            "Unlock password must contain only English letters and digits"
        )


class BoxUnlockPasswordIncorrectError(BaseException):
    status_code = 403

    def __init__(self, public_slug: str) -> None:
        self.public_slug = public_slug
        super().__init__(f"Incorrect unlock password for box: {public_slug!r}")


class BoxUnlockNotYetAvailableError(BaseException):
    status_code = 403

    def __init__(self, public_slug: str) -> None:
        self.public_slug = public_slug
        super().__init__(
            f"Box unlock password cannot be used before activation: {public_slug!r}"
        )


class BoxDesignNotAvailableError(BaseException):
    def __init__(self, design_id: uuid.UUID) -> None:
        self.design_id = design_id
        super().__init__(f"Box design is not available: {design_id}")
