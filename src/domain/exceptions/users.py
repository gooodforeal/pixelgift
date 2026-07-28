from src.domain.exceptions.base import BaseException


class UserNotFoundError(BaseException):
    def __init__(self, user_id: int = None) -> None:
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found!")


class TelegramIdInvalidError(BaseException):
    def __init__(self, telegram_id: str) -> None:
        self.telegram_id = telegram_id
        super().__init__(f"Telegram ID {telegram_id} is invalid!")
