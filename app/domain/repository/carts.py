"""Контракт персистентности корзины."""

from abc import ABC, abstractmethod
import uuid

from app.domain.entities.carts import Cart
from app.domain.repository.base import BaseRepository


class BaseCartsRepository(BaseRepository[Cart], ABC):
    """CRUD корзины и поиск по user_id."""

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> Cart | None: ...
