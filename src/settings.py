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
    jwt_access_token_ttl_minutes: int = 60 * 24

    login_challenge_ttl_minutes: int = 10


settings = Settings()
