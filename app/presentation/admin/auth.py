"""Аутентификация в SQLAdmin по логину и паролю из настроек."""

from __future__ import annotations

from hmac import compare_digest
from typing import Any

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.settings import settings

_SESSION_FLAG = "sqladmin"


class AdminAuth(AuthenticationBackend):
    """Сессионная проверка учётных данных `sqladmin_username` / `sqladmin_password`."""

    def __init__(self) -> None:
        super().__init__(
            secret_key=settings.sqladmin_secret_key,
            https_only=settings.sqladmin_cookie_secure,
            same_site=settings.sqladmin_cookie_samesite,
        )

    async def login(self, request: Request) -> bool:
        """Проверяет форму входа и помечает сессию как авторизованную."""
        form = await request.form()
        username = str(form.get("username") or "")
        password = str(form.get("password") or "")
        if not self._credentials_match(username, password):
            return False
        request.session[_SESSION_FLAG] = True
        request.session["user_id"] = settings.sqladmin_username
        return True

    async def logout(self, request: Request) -> bool:
        """Очищает сессию админки."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Возвращает True, если в сессии установлен флаг админ-входа."""
        return bool(request.session.get(_SESSION_FLAG))

    async def get_user_id(self, request: Request) -> Any:
        """Идентификатор пользователя для отображения в админке."""
        if not request.session.get(_SESSION_FLAG):
            return None
        return request.session.get("user_id") or settings.sqladmin_username

    @staticmethod
    def _credentials_match(username: str, password: str) -> bool:
        """Сравнивает логин и пароль с настройками через constant-time сравнение."""
        expected_user = settings.sqladmin_username
        expected_password = settings.sqladmin_password
        if not expected_user or not expected_password:
            return False
        return _digest_equal(username, expected_user) and _digest_equal(
            password,
            expected_password,
        )


def _digest_equal(actual: str, expected: str) -> bool:
    """Constant-time сравнение строк в UTF-8."""
    return compare_digest(actual.encode("utf-8"), expected.encode("utf-8"))
