from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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
    bot_api_secret: str = "dev-bot-api-secret"
    api_base_url: str = "http://localhost:8000"

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

    access_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
