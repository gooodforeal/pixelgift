from datetime import timedelta

from fastapi import Response

from src.settings import Settings


def set_access_cookie(response: Response, token: str, settings: Settings) -> None:
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
    response.delete_cookie(
        key=settings.access_cookie_name,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )


def clear_refresh_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )


def clear_auth_cookies(response: Response, settings: Settings) -> None:
    clear_access_cookie(response, settings)
    clear_refresh_cookie(response, settings)
