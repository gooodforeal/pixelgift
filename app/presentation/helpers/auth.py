"""Вспомогательные функции для JWT-cookie аутентификации."""

from datetime import timedelta

from fastapi import Response

from app.settings import Settings


def set_access_cookie(response: Response, token: str, settings: Settings) -> None:
    """Устанавливает HttpOnly cookie с access-токеном."""
    response.set_cookie(
        key=settings.access_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
        max_age=settings.jwt_access_token_ttl_minutes * 60,
    )


def set_refresh_cookie(response: Response, token: str, settings: Settings) -> None:
    """Устанавливает HttpOnly cookie с refresh-токеном."""
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
        max_age=int(
            timedelta(days=settings.jwt_refresh_token_ttl_days).total_seconds()
        ),
    )


def clear_access_cookie(response: Response, settings: Settings) -> None:
    """Удаляет cookie access-токена."""
    response.delete_cookie(
        key=settings.access_cookie_name,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )


def clear_refresh_cookie(response: Response, settings: Settings) -> None:
    """Удаляет cookie refresh-токена."""
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )


def clear_auth_cookies(response: Response, settings: Settings) -> None:
    """Удаляет обе auth-cookie."""
    clear_access_cookie(response, settings)
    clear_refresh_cookie(response, settings)
