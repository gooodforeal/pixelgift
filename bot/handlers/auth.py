from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

from bot.api_client import ApiClient
from src.presentation.schemas.auth import CompleteTelegramLoginRequest

router = Router(name="auth")
_api = ApiClient()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject) -> None:
    payload = (command.args or "").strip()

    if not payload:
        await message.answer(
            "Чтобы войти, нажмите «Войти через Telegram» на сайте."
        )
        return

    if not payload.startswith("login_"):
        await message.answer("Неизвестная команда. Войдите через сайт.")
        return

    code = payload.removeprefix("login_")
    if not code:
        await message.answer("Код входа пустой. Начните вход заново на сайте.")
        return

    if message.from_user is None:
        return

    try:
        result = await _api.complete_telegram_login(
            CompleteTelegramLoginRequest(
                code=code,
                telegram_id=message.from_user.id,
                first_name=message.from_user.first_name or "User",
                username=message.from_user.username,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
            )
        )
    except Exception:
        await message.answer(
            "Не удалось подтвердить вход. Попробуйте ещё раз позже."
        )
        return

    await message.answer(result.reply_text)
