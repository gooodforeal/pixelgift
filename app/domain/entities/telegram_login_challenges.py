"""Одноразовый код входа через Telegram-бота."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.values.telegram_id import TelegramId


class LoginChallengeStatus(StrEnum):
    """Жизненный цикл challenge от выдачи кода до использования или истечения."""

    PENDING = "pending"
    COMPLETED = "completed"
    CONSUMED = "consumed"
    EXPIRED = "expired"


@dataclass(frozen=False, kw_only=True)
class TelegramLoginChallenge(BaseEntity):
    """Challenge с кодом, сроком действия и привязкой к пользователю после подтверждения."""

    code: str
    status: LoginChallengeStatus
    expires_at: datetime
    telegram_id: TelegramId | None = None
    user_id: uuid.UUID | None = None
    completed_at: datetime | None = None
    client_ip_hash: str | None = None
