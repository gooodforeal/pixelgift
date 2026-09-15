import logging

import httpx

from src.application.ports.notifications import BaseTelegramNotifier
from src.settings import Settings

logger = logging.getLogger(__name__)


class TelegramBotNotifier(BaseTelegramNotifier):
    def __init__(self, settings: Settings) -> None:
        self._token = settings.telegram_bot_token

    async def send_message(self, *, telegram_id: int, text: str) -> None:
        if not self._token:
            logger.warning("Telegram bot token is empty, skip notification")
            return

        await self._post(
            "sendMessage",
            json={"chat_id": telegram_id, "text": text, "parse_mode": "HTML"},
        )

    async def send_photo(
        self,
        *,
        telegram_id: int,
        photo: bytes,
        filename: str,
        caption: str,
    ) -> None:
        if not self._token:
            logger.warning("Telegram bot token is empty, skip notification")
            return

        await self._post(
            "sendPhoto",
            data={
                "chat_id": str(telegram_id),
                "caption": caption,
                "parse_mode": "HTML",
            },
            files={"photo": (filename, photo, "image/png")},
        )

    async def _post(
        self,
        method: str,
        *,
        json: dict[str, object] | None = None,
        data: dict[str, str] | None = None,
        files: dict[str, tuple[str, bytes, str]] | None = None,
    ) -> None:
        url = f"https://api.telegram.org/bot{self._token}/{method}"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, json=json, data=data, files=files)
            response.raise_for_status()
