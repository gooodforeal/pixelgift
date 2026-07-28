from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.application.dto.auth import (
    CompleteTelegramLoginCommand,
    PollTelegramLoginCommand,
    StartTelegramLoginCommand,
)
from src.application.use_cases.auth import (
    CompleteTelegramLoginUseCase,
    PollTelegramLoginStatusUseCase,
    StartTelegramLoginUseCase,
)
from src.domain.exceptions.auth import (
    LoginChallengeNotFoundError,
    UserInactiveError,
)
from src.presentation.deps import (
    get_complete_telegram_login_uc,
    get_current_user_id,
    get_poll_telegram_login_uc,
    get_start_telegram_login_uc,
    verify_bot_api_secret,
)
from src.presentation.schemas.auth import (
    CompleteTelegramLoginRequest,
    CompleteTelegramLoginResponse,
    TelegramLoginStartResponse,
    TelegramLoginStatusResponse,
)

router = APIRouter(tags=["auth"])


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
    uc: PollTelegramLoginStatusUseCase = Depends(get_poll_telegram_login_uc),
) -> TelegramLoginStatusResponse:
    try:
        result = await uc.execute(PollTelegramLoginCommand(code=code))
    except LoginChallengeNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserInactiveError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return TelegramLoginStatusResponse(
        status=result.status,
        access_token=result.access_token,
        token_type=result.token_type,
        user_id=result.user_id,
    )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(_user_id=Depends(get_current_user_id)) -> None:
    return None


@router.post(
    "/auth/telegram/webhook",
    response_model=CompleteTelegramLoginResponse,
)
async def create_telegram_login(
    body: CompleteTelegramLoginRequest,
    _: None = Depends(verify_bot_api_secret),
    uc: CompleteTelegramLoginUseCase = Depends(get_complete_telegram_login_uc),
) -> CompleteTelegramLoginResponse:
    """Called by the aiogram bot process — not by the browser."""
    result = await uc.execute(
        CompleteTelegramLoginCommand(
            code=body.code,
            telegram_id=body.telegram_id,
            first_name=body.first_name,
            username=body.username,
            last_name=body.last_name,
            language_code=body.language_code,
        )
    )
    return CompleteTelegramLoginResponse(ok=result.ok, reply_text=result.reply_text)
