from base64 import b64decode
import binascii
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from src.application.dto.auth import (
    CompleteTelegramLoginCommand,
    LogoutCommand,
    PollTelegramLoginCommand,
    RefreshAccessTokenCommand,
    StartTelegramLoginCommand,
)
from src.application.use_cases.auth import (
    CompleteTelegramLoginUseCase,
    LogoutUseCase,
    PollTelegramLoginStatusUseCase,
    RefreshAccessTokenUseCase,
    StartTelegramLoginUseCase,
)
from src.application.use_cases.queries import GetCurrentUserUseCase, GetUserAvatarUseCase
from src.domain.exceptions.auth import (
    InvalidRefreshTokenError,
    LoginChallengeNotFoundError,
    UserInactiveError,
)
from src.domain.exceptions.users import UserNotFoundError
from src.presentation.deps.auth import (
    get_complete_telegram_login_uc,
    get_current_user_id,
    get_logout_uc,
    get_poll_telegram_login_uc,
    get_refresh_access_token_uc,
    get_start_telegram_login_uc,
    verify_bot_api_secret,
)
from src.presentation.deps.common import get_settings
from src.presentation.deps.users import get_current_user_uc, get_user_avatar_uc
from src.presentation.helpers.auth import (
    clear_auth_cookies,
    set_access_cookie,
    set_refresh_cookie,
)
from src.presentation.schemas.auth import (
    AccessTokenResponse,
    CompleteTelegramLoginRequest,
    CompleteTelegramLoginResponse,
    CurrentUserResponse,
    TelegramLoginStartResponse,
    TelegramLoginStatusResponse,
)
from src.settings import Settings

router = APIRouter(tags=["auth"])

_MAX_AVATAR_BYTES = 2 * 1024 * 1024


@router.post("/auth/telegram/start", response_model=TelegramLoginStartResponse)
async def start_telegram_login(
    request: Request,
    uc: StartTelegramLoginUseCase = Depends(get_start_telegram_login_uc),
) -> TelegramLoginStartResponse:
    client_ip = request.client.host if request.client else None
    result = await uc.execute(StartTelegramLoginCommand(client_ip_hash=client_ip))
    return TelegramLoginStartResponse(
        code=result.code,
        bot_url=result.bot_url,
        expires_at=result.expires_at,
    )


@router.get("/auth/telegram/status", response_model=TelegramLoginStatusResponse)
async def telegram_login_status(
    code: str,
    request: Request,
    uc: PollTelegramLoginStatusUseCase = Depends(get_poll_telegram_login_uc),
    cfg: Settings = Depends(get_settings),
) -> Response:
    try:
        result = await uc.execute(
            PollTelegramLoginCommand(
                code=code,
                user_agent=request.headers.get("user-agent"),
                client_ip=request.client.host if request.client else None,
            )
        )
    except LoginChallengeNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserInactiveError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    payload = TelegramLoginStatusResponse(
        status=result.status,
        access_token=None,
        token_type=result.token_type,
        user_id=result.user_id,
    )
    response = JSONResponse(content=payload.model_dump(mode="json"))
    if result.access_token and result.refresh_token:
        set_access_cookie(response, result.access_token, cfg)
        set_refresh_cookie(response, result.refresh_token, cfg)
    return response


@router.post("/auth/refresh", response_model=AccessTokenResponse)
async def refresh_access_token(
    request: Request,
    uc: RefreshAccessTokenUseCase = Depends(get_refresh_access_token_uc),
    cfg: Settings = Depends(get_settings),
) -> Response:
    raw = request.cookies.get(cfg.refresh_cookie_name)
    if not raw:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    try:
        result = await uc.execute(
            RefreshAccessTokenCommand(
                refresh_token=raw,
                user_agent=request.headers.get("user-agent"),
                client_ip=request.client.host if request.client else None,
            )
        )
    except InvalidRefreshTokenError as exc:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )
        clear_auth_cookies(response, cfg)
        return response
    except UserInactiveError as exc:
        response = JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )
        clear_auth_cookies(response, cfg)
        return response

    payload = AccessTokenResponse(
        token_type=result.token_type,
        user_id=result.user_id,
    )
    response = JSONResponse(content=payload.model_dump(mode="json"))
    set_access_cookie(response, result.access_token, cfg)
    set_refresh_cookie(response, result.refresh_token, cfg)
    return response


@router.get("/auth/me", response_model=CurrentUserResponse)
async def get_current_user(
    user_id=Depends(get_current_user_id),
    uc: GetCurrentUserUseCase = Depends(get_current_user_uc),
) -> CurrentUserResponse:
    try:
        user = await uc.execute(user_id=user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserInactiveError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return CurrentUserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        language_code=user.language_code,
        photo_url=f"/users/{user.id}/avatar" if user.photo_url else None,
        is_admin=user.is_admin,
        created_at=user.created_at.isoformat(),
        last_seen_at=user.last_seen_at.isoformat() if user.last_seen_at else None,
    )


@router.get("/users/{user_id}/avatar")
async def get_user_avatar(
    user_id: uuid.UUID,
    uc: GetUserAvatarUseCase = Depends(get_user_avatar_uc),
) -> Response:
    try:
        content = await uc.execute(user_id=user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Avatar not found") from exc

    return Response(
        content=content.data,
        media_type=content.mime_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    uc: LogoutUseCase = Depends(get_logout_uc),
    cfg: Settings = Depends(get_settings),
) -> Response:
    raw = request.cookies.get(cfg.refresh_cookie_name)
    await uc.execute(LogoutCommand(refresh_token=raw))
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_auth_cookies(response, cfg)
    return response


@router.post(
    "/auth/telegram/webhook",
    response_model=CompleteTelegramLoginResponse,
)
async def create_telegram_login(
    body: CompleteTelegramLoginRequest,
    _: None = Depends(verify_bot_api_secret),
    uc: CompleteTelegramLoginUseCase = Depends(get_complete_telegram_login_uc),
) -> CompleteTelegramLoginResponse:
    photo_bytes: bytes | None = None
    if body.photo_base64:
        try:
            photo_bytes = b64decode(body.photo_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Invalid photo_base64",
            ) from exc
        if len(photo_bytes) > _MAX_AVATAR_BYTES:
            photo_bytes = None

    result = await uc.execute(
        CompleteTelegramLoginCommand(
            code=body.code,
            telegram_id=body.telegram_id,
            first_name=body.first_name,
            username=body.username,
            last_name=body.last_name,
            language_code=body.language_code,
            photo_bytes=photo_bytes,
            photo_content_type=body.photo_content_type or "image/jpeg",
        )
    )
    return CompleteTelegramLoginResponse(ok=result.ok, reply_text=result.reply_text)
