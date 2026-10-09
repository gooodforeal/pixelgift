"""Контракт персистентности сессий пользователя."""

from abc import ABC, abstractmethod
import uuid

from app.domain.entities.user_sessions import UserSession
from app.domain.repository.base import BaseRepository


class BaseUserSessionsRepository(BaseRepository[UserSession], ABC):
    """Поиск сессии по хешу refresh-токена и список сессий пользователя."""

    @abstractmethod
    async def get_by_refresh_token_hash(
        self, refresh_token_hash: str
    ) -> UserSession | None: ...

    @abstractmethod
    async def list_by_user_id(self, user_id: uuid.UUID) -> list[UserSession]: ...
