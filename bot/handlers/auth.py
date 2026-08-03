import asyncio
from base64 import b64encode

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

from bot.api_client import ApiClient
from bot.schemas import CompleteTelegramLoginRequest

router = Router(name="auth")
_api = ApiClient()

_PHOTO_TIMEOUT_SEC = 5.0


async def _download_profile_photo(message: Message) -> tuple[bytes, str] | None:
    if message.from_user is None or message.bot is None:
        return None

    try:
        photos = await message.bot.get_user_profile_photos(message.from_user.id, limit=1)
        if photos.total_count <= 0 or not photos.photos:
            return None

        best = photos.photos[0][-1]
        file = await message.bot.get_file(best.file_id)
        if not file.file_path:
            return None

        buffer = await message.bot.download_file(file.file_path)
        if buffer is None:
            return None

        if hasattr(buffer, "seek"):
            buffer.seek(0)
        data = buffer.read() if hasattr(buffer, "read") else bytes(buffer)
        if not data:
            return None
        return data, "image/jpeg"
    except Exception:
        return None


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
        photo = await asyncio.wait_for(
            _download_profile_photo(message),
            timeout=_PHOTO_TIMEOUT_SEC,
        )
    except asyncio.TimeoutError:
        photo = None

    photo_base64 = b64encode(photo[0]).decode("ascii") if photo else None
    photo_content_type = photo[1] if photo else None

    try:
        result = await _api.complete_telegram_login(
            CompleteTelegramLoginRequest(
                code=code,
                telegram_id=message.from_user.id,
                first_name=message.from_user.first_name or "User",
                username=message.from_user.username,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
                photo_base64=photo_base64,
                photo_content_type=photo_content_type,
            )
        )
    except Exception:
        await message.answer(
            "Не удалось подтвердить вход. Попробуйте ещё раз позже."
        )
        return

    await message.answer(result.reply_text)
