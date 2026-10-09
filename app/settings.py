"""Конфигурация приложения из переменных окружения и `.env`."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    """Параметры API, интеграций и инфраструктуры Pixelgift."""
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/pixelgift"
    )

    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "pixelgift"
    minio_region: str = "us-east-1"

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    support_telegram_url: str = "https://t.me/pixelgift_auth_bot"
    bot_api_secret: str = "dev-bot-api-secret"
    api_base_url: str = "http://localhost:8080/api"

    jwt_secret: str = "dev-change-me-to-a-long-random-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_ttl_minutes: int = 15
    jwt_refresh_token_ttl_days: int = 30

    cookie_secure: bool = False

    login_challenge_ttl_minutes: int = 10

    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    public_web_url: str = "http://localhost:8080"
    redis_url: str = "redis://localhost:6379/0"

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "PixelGift <noreply@pixelgift.local>"
    smtp_use_tls: bool = False

    # Total send attempts per notification job (1 first try + retries).
    notification_max_attempts: int = 2
    # Reclaim jobs stuck in processing longer than this (minutes).
    notification_processing_stale_minutes: int = 10

    access_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"

    sqladmin_username: str = "admin"
    sqladmin_password: str = "admin"
    sqladmin_secret_key: str = "dev-sqladmin-session-secret"
    sqladmin_cookie_secure: bool = False
    sqladmin_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    # OpenAI-compatible LLM (box editor assistant)
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 60
    llm_assistant_max_messages: int = 20
    # Optional HTTP(S) proxy for LLM calls only.
    # Examples: http://host:7890  or  http://user:password@host:7890
    # URL-encode special chars in user/password (@ → %40, : → %3A).
    llm_proxy_url: str = ""

    # YooKassa (test/live keys via env)
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    yookassa_return_url: str = "http://localhost:8080/app/profile"
    yookassa_timeout_seconds: float = 30

    @property
    def cors_origins_list(self) -> list[str]:
        """Список разрешённых CORS origins из строки `cors_origins`."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
