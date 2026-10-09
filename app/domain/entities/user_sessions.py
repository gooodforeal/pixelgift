"""Сессия пользователя с refresh-токеном."""

from dataclasses import dataclass
from datetime import datetime
import uuid

from app.domain.entities.base import BaseEntity


@dataclass(frozen=False, kw_only=True)
class UserSession(BaseEntity):
    """Хранит хеш refresh-токена, срок жизни и признак отзыва."""

    user_id: uuid.UUID
    refresh_token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None
    user_agent: str | None = None
    ip_hash: str | None = None
