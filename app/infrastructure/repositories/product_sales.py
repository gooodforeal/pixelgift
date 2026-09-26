import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.product_sales import ProductSale
from app.domain.repository.product_sales import BaseProductSalesRepository
from app.infrastructure.mappers.product_sales import (
    apply_product_sale,
    product_sale_to_entity,
    product_sale_to_model,
)
from app.infrastructure.models.product_sales import ProductSaleModel


class SqlAlchemyProductSalesRepository(BaseProductSalesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: ProductSale) -> None:
        self._session.add(product_sale_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> ProductSale | None:
        model = await self._session.get(ProductSaleModel, id_)
        return product_sale_to_entity(model) if model is not None else None

    async def update(self, entity: ProductSale) -> ProductSale:
        model = await self._session.get(ProductSaleModel, entity.id)
        if model is None:
            raise ValueError(f"ProductSale not found: {entity.id}")
        apply_product_sale(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(ProductSaleModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_product_id(self, product_id: uuid.UUID) -> ProductSale | None:
        result = await self._session.execute(
            select(ProductSaleModel).where(ProductSaleModel.product_id == product_id)
        )
        model = result.scalar_one_or_none()
        return product_sale_to_entity(model) if model is not None else None

    async def list_by_product_ids(
        self, product_ids: list[uuid.UUID]
    ) -> list[ProductSale]:
        if not product_ids:
            return []
        result = await self._session.execute(
            select(ProductSaleModel).where(
                ProductSaleModel.product_id.in_(product_ids)
            )
        )
        return [product_sale_to_entity(m) for m in result.scalars().all()]

    async def list_active_by_product_ids(
        self, product_ids: list[uuid.UUID]
    ) -> list[ProductSale]:
        if not product_ids:
            return []
        result = await self._session.execute(
            select(ProductSaleModel).where(
                ProductSaleModel.product_id.in_(product_ids),
                ProductSaleModel.is_active.is_(True),
            )
        )
        return [product_sale_to_entity(m) for m in result.scalars().all()]
