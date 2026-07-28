from abc import ABC, abstractmethod
import uuid

from src.domain.entities.user_sessions import UserSession
from src.domain.repository.base import BaseRepository


class BaseUserSessionsRepository(BaseRepository[UserSession], ABC):
    @abstractmethod
    async def get_by_refresh_token_hash(
        self, refresh_token_hash: str
    ) -> UserSession | None: ...

    @abstractmethod
    async def list_by_user_id(self, user_id: uuid.UUID) -> list[UserSession]: ...
