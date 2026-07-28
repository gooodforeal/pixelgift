from aiogram import Dispatcher

from bot.handlers.auth import router as auth_router


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(auth_router)
    return dp
