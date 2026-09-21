from __future__ import annotations

from hmac import compare_digest
from typing import Any

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.settings import settings

_SESSION_FLAG = "sqladmin"


class AdminAuth(AuthenticationBackend):
    def __init__(self) -> None:
        super().__init__(
            secret_key=settings.sqladmin_secret_key,
            https_only=settings.sqladmin_cookie_secure,
            same_site=settings.sqladmin_cookie_samesite,
        )

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username") or "")
        password = str(form.get("password") or "")
        if not self._credentials_match(username, password):
            return False
        request.session[_SESSION_FLAG] = True
        request.session["user_id"] = settings.sqladmin_username
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get(_SESSION_FLAG))

    async def get_user_id(self, request: Request) -> Any:
        if not request.session.get(_SESSION_FLAG):
            return None
        return request.session.get("user_id") or settings.sqladmin_username

    @staticmethod
    def _credentials_match(username: str, password: str) -> bool:
        expected_user = settings.sqladmin_username
        expected_password = settings.sqladmin_password
        if not expected_user or not expected_password:
            return False
        return _digest_equal(username, expected_user) and _digest_equal(
            password,
            expected_password,
        )


def _digest_equal(actual: str, expected: str) -> bool:
    return compare_digest(actual.encode("utf-8"), expected.encode("utf-8"))
