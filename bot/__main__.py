import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError

from bot.app import create_dispatcher
from bot.settings import bot_settings

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("bot")


async def _prepare_polling(bot: Bot) -> None:
    """Clear webhook with retries; keep pending updates so login /start is not lost."""
    delay = 2.0
    for attempt in range(1, 8):
        try:
            await bot.delete_webhook(drop_pending_updates=False)
            return
        except TelegramNetworkError as exc:
            logger.warning(
                "delete_webhook failed (attempt %s/7): %s", attempt, exc
            )
            if attempt == 7:
                raise
            await asyncio.sleep(delay)
            delay = min(delay * 1.5, 15.0)


async def run() -> None:
    if not bot_settings.telegram_bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(
        token=bot_settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()

    await _prepare_polling(bot)
    logger.info(
        "Starting aiogram bot polling as @%s → API %s",
        bot_settings.telegram_bot_username or "unknown",
        bot_settings.api_base_url,
    )
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
