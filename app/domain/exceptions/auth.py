"""Ошибки входа через Telegram challenge и сессий."""

from app.domain.exceptions.base import BaseException
import uuid


class LoginChallengeNotFoundError(BaseException):
    """Challenge логина не найден."""
    status_code = 404

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Login challenge not found: {code!r}")


class LoginChallengeExpiredError(BaseException):
    """Challenge логина истёк."""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Login challenge expired: {code!r}")


class LoginChallengeAlreadyUsedError(BaseException):
    """Challenge логина уже использован."""
    status_code = 409

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Login challenge already used: {code!r}")


class LoginChallengeInvalidError(BaseException):
    """Challenge логина невалиден."""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Login challenge is invalid: {code!r}")


class UserInactiveError(BaseException):
    """Пользователь деактивирован."""
    status_code = 403

    def __init__(self, user_id: uuid.UUID) -> None:
        self.user_id = user_id
        super().__init__(f"User is inactive: {user_id}")


class InvalidRefreshTokenError(BaseException):
    """Невалидный или просроченный refresh-токен."""
    status_code = 401

    def __init__(self) -> None:
        super().__init__("Invalid or expired refresh token")
