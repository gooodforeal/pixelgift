from abc import ABC, abstractmethod
import uuid

from app.domain.entities.orders import Order
from app.domain.repository.base import BaseRepository


class BaseOrdersRepository(BaseRepository[Order], ABC):
    @abstractmethod
    async def get_by_provider_payment_id(
        self, provider_payment_id: str
    ) -> Order | None: ...

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: str) -> Order | None: ...

    @abstractmethod
    async def list_pending_by_user_id(
        self, user_id: uuid.UUID, *, limit: int = 20
    ) -> list[Order]: ...

    @abstractmethod
    async def list_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[Order]: ...

    @abstractmethod
    async def count_by_user_id(self, user_id: uuid.UUID) -> int: ...
