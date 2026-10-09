"""Схемы аутентификации и профиля пользователя."""

from base64 import b64decode
import binascii
import uuid

from pydantic import BaseModel, field_validator

from app.presentation.schemas.base import BaseResponseSchema


class TelegramLoginStartSchema(BaseModel):
    """Данные для начала входа через Telegram."""
    code: str
    bot_url: str
    expires_at: str


class TelegramLoginStartResponse(BaseResponseSchema[TelegramLoginStartSchema]):
    """Ответ POST /auth/telegram/start."""
    pass


class TelegramLoginStatusSchema(BaseModel):
    """Статус ожидания или завершения логина."""
    status: str
    access_token: str | None = None
    token_type: str | None = None
    user_id: uuid.UUID | None = None


class TelegramLoginStatusResponse(BaseResponseSchema[TelegramLoginStatusSchema]):
    """Ответ GET /auth/telegram/status."""
    pass


class AccessTokenSchema(BaseModel):
    """Метаданные access-токена после refresh."""
    token_type: str = "bearer"
    user_id: uuid.UUID | None = None


class AccessTokenResponse(BaseResponseSchema[AccessTokenSchema]):
    """Ответ POST /auth/refresh."""
    pass


class CompleteTelegramLoginRequest(BaseModel):
    """Тело webhook бота о завершении логина."""
    code: str
    telegram_id: int
    first_name: str
    username: str | None = None
    last_name: str | None = None
    language_code: str | None = None
    photo_base64: str | None = None
    photo_content_type: str | None = None

    @field_validator("photo_base64")
    @classmethod
    def validate_photo_base64(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("Invalid photo_base64") from exc
        return value


class CompleteTelegramLoginSchema(BaseModel):
    """Результат завершения логина для бота."""
    ok: bool
    reply_text: str


class CompleteTelegramLoginResponse(BaseResponseSchema[CompleteTelegramLoginSchema]):
    """Ответ POST /auth/telegram/webhook."""
    pass


class CurrentUserSchema(BaseModel):
    """Профиль авторизованного пользователя."""
    id: uuid.UUID
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    photo_url: str | None = None
    is_admin: bool = False
    notifications_enabled: bool = True
    created_at: str
    last_seen_at: str | None = None


class CurrentUserResponse(BaseResponseSchema[CurrentUserSchema]):
    """Ответ GET/PATCH /auth/me."""
    pass


class UpdateCurrentUserSettingsRequest(BaseModel):
    """Частичное обновление настроек пользователя."""
    notifications_enabled: bool | None = None
