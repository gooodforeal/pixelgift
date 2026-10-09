"""Команды и результаты аутентификации через Telegram."""

from dataclasses import dataclass
import uuid


@dataclass(frozen=True, kw_only=True)
class StartTelegramLoginCommand:
    """Старт сценария входа: создаётся одноразовый код."""

    client_ip_hash: str | None = None


@dataclass(frozen=True, kw_only=True)
class PollTelegramLoginCommand:
    """Опрос статуса челленджа и выдача токенов после подтверждения в боте."""

    code: str
    user_agent: str | None = None
    client_ip: str | None = None


@dataclass(frozen=True, kw_only=True)
class CompleteTelegramLoginCommand:
    """Завершение входа из Telegram-бота по коду и данным пользователя."""

    code: str
    telegram_id: int
    first_name: str
    username: str | None = None
    last_name: str | None = None
    language_code: str | None = None
    photo_bytes: bytes | None = None
    photo_content_type: str | None = None


@dataclass(frozen=True, kw_only=True)
class RefreshAccessTokenCommand:
    """Обмен действующего refresh-токена на новую пару токенов."""

    refresh_token: str
    user_agent: str | None = None
    client_ip: str | None = None


@dataclass(frozen=True, kw_only=True)
class LogoutCommand:
    """Отзыв сессии по refresh-токену."""

    refresh_token: str | None = None


@dataclass(frozen=True, kw_only=True)
class UpdateCurrentUserSettingsCommand:
    """Обновление настроек текущего пользователя."""

    user_id: uuid.UUID
    notifications_enabled: bool | None = None


@dataclass(frozen=True, kw_only=True)
class TelegramLoginStartResult:
    """Код входа, deep-link в бота и время истечения."""

    code: str
    bot_url: str
    expires_at: str


@dataclass(frozen=True, kw_only=True)
class TelegramLoginStatusResult:
    """Статус челленджа; при успехе — JWT и refresh."""

    status: str
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    user_id: uuid.UUID | None = None


@dataclass(frozen=True, kw_only=True)
class TokenPairResult:
    """Access- и refresh-токены после refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID | None = None


@dataclass(frozen=True, kw_only=True)
class CompleteLoginResult:
    """Ответ боту: успех и текст для пользователя."""

    ok: bool
    reply_text: str
