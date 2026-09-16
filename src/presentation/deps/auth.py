from __future__ import annotations

import uuid

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services.jwt import JwtService
from src.application.use_cases.auth import (
    CompleteTelegramLoginUseCase,
    LogoutUseCase,
    PollTelegramLoginStatusUseCase,
    RefreshAccessTokenUseCase,
    StartTelegramLoginUseCase,
)
from src.infrastructure.storage.s3_storage import S3ObjectStorage
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.presentation.deps.common import get_jwt_service, get_settings, get_storage
from src.settings import Settings

_bearer = HTTPBearer(auto_error=False)


def get_start_telegram_login_uc(
    cfg: Settings = Depends(get_settings),
) -> StartTelegramLoginUseCase:
    return StartTelegramLoginUseCase(SqlAlchemyUnitOfWork(), cfg)


def get_poll_telegram_login_uc(
    jwt_service: JwtService = Depends(get_jwt_service),
    cfg: Settings = Depends(get_settings),
) -> PollTelegramLoginStatusUseCase:
    return PollTelegramLoginStatusUseCase(SqlAlchemyUnitOfWork(), jwt_service, cfg)


def get_refresh_access_token_uc(
    jwt_service: JwtService = Depends(get_jwt_service),
    cfg: Settings = Depends(get_settings),
) -> RefreshAccessTokenUseCase:
    return RefreshAccessTokenUseCase(SqlAlchemyUnitOfWork(), jwt_service, cfg)


def get_logout_uc() -> LogoutUseCase:
    return LogoutUseCase(SqlAlchemyUnitOfWork())


def get_complete_telegram_login_uc(
    storage: S3ObjectStorage = Depends(get_storage),
    cfg: Settings = Depends(get_settings),
) -> CompleteTelegramLoginUseCase:
    return CompleteTelegramLoginUseCase(
        SqlAlchemyUnitOfWork(),
        storage,
        api_base_url=cfg.api_base_url,
    )


def _decode_user_id(jwt_service: JwtService, raw_token: str | None) -> uuid.UUID:
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = jwt_service.decode_access_token(raw_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    return payload.user_id


async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    jwt_service: JwtService = Depends(get_jwt_service),
    cfg: Settings = Depends(get_settings),
) -> uuid.UUID:
    raw: str | None = None
    if credentials is not None and credentials.scheme.lower() == "bearer":
        raw = credentials.credentials
    if not raw:
        raw = request.cookies.get(cfg.access_cookie_name)
    return _decode_user_id(jwt_service, raw)


async def get_optional_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    jwt_service: JwtService = Depends(get_jwt_service),
    cfg: Settings = Depends(get_settings),
) -> uuid.UUID | None:
    raw: str | None = None
    if credentials is not None and credentials.scheme.lower() == "bearer":
        raw = credentials.credentials
    if not raw:
        raw = request.cookies.get(cfg.access_cookie_name)
    if not raw:
        return None
    try:
        return _decode_user_id(jwt_service, raw)
    except HTTPException:
        return None


async def verify_bot_api_secret(
    x_bot_api_secret: str | None = Header(default=None),
    cfg: Settings = Depends(get_settings),
) -> None:
    expected = cfg.bot_api_secret
    if not expected or x_bot_api_secret != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid bot API secret",
        )
