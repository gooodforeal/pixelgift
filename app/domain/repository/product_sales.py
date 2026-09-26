from abc import ABC, abstractmethod
import uuid

from app.domain.entities.product_sales import ProductSale
from app.domain.repository.base import BaseRepository


class BaseProductSalesRepository(BaseRepository[ProductSale], ABC):
    @abstractmethod
    async def get_by_product_id(self, product_id: uuid.UUID) -> ProductSale | None: ...

    @abstractmethod
    async def list_by_product_ids(
        self, product_ids: list[uuid.UUID]
    ) -> list[ProductSale]: ...

    @abstractmethod
    async def list_active_by_product_ids(
        self, product_ids: list[uuid.UUID]
    ) -> list[ProductSale]: ...
