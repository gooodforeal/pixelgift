from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Settings for the aiogram bot process (no DB access)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    api_base_url: str = "http://localhost:8000"
    bot_api_secret: str = "dev-bot-api-secret"


bot_settings = BotSettings()
