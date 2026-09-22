from app.domain.exceptions.base import BaseException
import uuid


class UserNotFoundError(BaseException):
    status_code = 404

    def __init__(self, user_id: uuid.UUID | None = None) -> None:
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found!")


class TelegramIdError(BaseException):
    """Базовая ошибка валидации Telegram ID."""


class TelegramIdNotNumericError(TelegramIdError):
    def __init__(self, telegram_id: str) -> None:
        self.telegram_id = telegram_id
        super().__init__(f"Telegram ID {telegram_id!r} is not numeric")


class TelegramIdNonPositiveError(TelegramIdError):
    def __init__(self, telegram_id: str) -> None:
        self.telegram_id = telegram_id
        super().__init__(f"Telegram ID {telegram_id!r} must be positive")


class TelegramIdTooLongError(TelegramIdError):
    def __init__(self, telegram_id: str) -> None:
        self.telegram_id = telegram_id
        super().__init__(f"Telegram ID {telegram_id!r} is too long")
