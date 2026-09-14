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

        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                url,
                json={"chat_id": telegram_id, "text": text},
            )
            response.raise_for_status()
