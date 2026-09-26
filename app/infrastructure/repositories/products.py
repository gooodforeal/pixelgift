import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.products import Product
from app.domain.repository.products import BaseProductsRepository
from app.infrastructure.mappers.products import (
    apply_product,
    product_to_entity,
    product_to_model,
)
from app.infrastructure.models.products import ProductModel


class SqlAlchemyProductsRepository(BaseProductsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: Product) -> None:
        self._session.add(product_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> Product | None:
        model = await self._session.get(ProductModel, id_)
        return product_to_entity(model) if model is not None else None

    async def update(self, entity: Product) -> Product:
        model = await self._session.get(ProductModel, entity.id)
        if model is None:
            raise ValueError(f"Product not found: {entity.id}")
        apply_product(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(ProductModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_sku(self, sku: str) -> Product | None:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.sku == sku)
        )
        model = result.scalar_one_or_none()
        return product_to_entity(model) if model is not None else None

    async def list_active(self) -> list[Product]:
        result = await self._session.execute(
            select(ProductModel)
            .where(ProductModel.is_active.is_(True))
            .order_by(ProductModel.name.asc())
        )
        return [product_to_entity(m) for m in result.scalars().all()]

    async def list_all(self) -> list[Product]:
        result = await self._session.execute(
            select(ProductModel).order_by(ProductModel.created_at.desc())
        )
        return [product_to_entity(m) for m in result.scalars().all()]

    async def list_by_ids(self, ids: list[uuid.UUID]) -> list[Product]:
        if not ids:
            return []
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id.in_(ids))
        )
        return [product_to_entity(m) for m in result.scalars().all()]
