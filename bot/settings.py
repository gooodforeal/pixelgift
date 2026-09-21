from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Локальный (не-docker) запуск: опциональный bot/.env.
# В docker переменные приходят из docker/bot/.env через env_file.
_ENV_FILE = Path(__file__).resolve().parent / ".env"


class BotSettings(BaseSettings):
    """Settings for the aiogram bot process (no DB access)."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    api_base_url: str = "http://localhost:8080/api"
    bot_api_secret: str = "dev-bot-api-secret"


bot_settings = BotSettings()
