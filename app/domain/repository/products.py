"""Контракт персистентности товаров каталога."""

from abc import ABC, abstractmethod
import uuid

from app.domain.entities.products import Product
from app.domain.repository.base import BaseRepository


class BaseProductsRepository(BaseRepository[Product], ABC):
    """Выборка товаров по SKU, id и спискам активных записей."""

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Product | None: ...

    @abstractmethod
    async def list_active(self) -> list[Product]: ...

    @abstractmethod
    async def list_all(self) -> list[Product]: ...

    @abstractmethod
    async def list_by_ids(self, ids: list[uuid.UUID]) -> list[Product]: ...
