from abc import ABC, abstractmethod
import uuid

from app.domain.entities.user_balance_logs import UserBalanceLog
from app.domain.repository.base import BaseRepository


class BaseUserBalanceLogsRepository(BaseRepository[UserBalanceLog], ABC):
    @abstractmethod
    async def get_by_reason_reference(
        self,
        *,
        reason: str,
        reference_type: str,
        reference_id: uuid.UUID,
    ) -> UserBalanceLog | None: ...

    @abstractmethod
    async def list_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[UserBalanceLog]: ...

    @abstractmethod
    async def count_by_user_id(self, user_id: uuid.UUID) -> int: ...
