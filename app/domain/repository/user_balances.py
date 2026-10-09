"""Контракт персистентности балансов пользователя."""

from abc import ABC, abstractmethod
import uuid

from app.domain.entities.user_balances import UserBalance
from app.domain.repository.base import BaseRepository


class BaseUserBalancesRepository(BaseRepository[UserBalance], ABC):
    """Баланс по паре user_id + product_id и список всех балансов пользователя."""

    @abstractmethod
    async def get_by_user_and_product(
        self, *, user_id: uuid.UUID, product_id: uuid.UUID
    ) -> UserBalance | None: ...

    @abstractmethod
    async def list_by_user_id(self, user_id: uuid.UUID) -> list[UserBalance]: ...
