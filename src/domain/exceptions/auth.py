from src.domain.exceptions.base import BaseException
import uuid


class LoginChallengeNotFoundError(BaseException):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Login challenge not found: {code!r}")


class LoginChallengeExpiredError(BaseException):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Login challenge expired: {code!r}")


class LoginChallengeAlreadyUsedError(BaseException):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Login challenge already used: {code!r}")


class LoginChallengeInvalidError(BaseException):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Login challenge is invalid: {code!r}")


class UserInactiveError(BaseException):
    def __init__(self, user_id: uuid.UUID) -> None:
        self.user_id = user_id
        super().__init__(f"User is inactive: {user_id}")


class InvalidRefreshTokenError(BaseException):
    def __init__(self) -> None:
        super().__init__("Invalid or expired refresh token")
