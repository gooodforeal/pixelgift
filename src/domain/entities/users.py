from dataclasses import dataclass
from datetime import datetime

from src.domain.entities.base import BaseEntity
from src.domain.values.telegram_id import TelegramId
from src.domain.values.url import Url


@dataclass(frozen=False, kw_only=True)
class User(BaseEntity):
    telegram_id: TelegramId
    first_name: str
    username: str | None = None
    last_name: str | None = None
    language_code: str | None = None
    photo_url: Url | None = None
    is_active: bool = True
    last_seen_at: datetime | None = None
    is_admin: bool = False
