import httpx

from bot.settings import BotSettings, bot_settings
from src.presentation.schemas.auth import (
    CompleteTelegramLoginRequest,
    CompleteTelegramLoginResponse,
)


class ApiClient:
    def __init__(self, settings: BotSettings | None = None) -> None:
        self._settings = settings or bot_settings

    async def complete_telegram_login(
        self, payload: CompleteTelegramLoginRequest
    ) -> CompleteTelegramLoginResponse:
        url = (
            self._settings.api_base_url.rstrip("/")
            + "/auth/telegram/webhook"
        )
        headers = {"X-Bot-Api-Secret": self._settings.bot_api_secret}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=payload.model_dump(),
                headers=headers,
            )
            response.raise_for_status()
            return CompleteTelegramLoginResponse.model_validate(response.json())
