"""SQLAlchemy-репозиторий корзин."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.carts import Cart
from app.domain.repository.carts import BaseCartsRepository
from app.infrastructure.mappers.carts import apply_cart, cart_to_entity, cart_to_model
from app.infrastructure.models.carts import CartModel


class SqlAlchemyCartsRepository(BaseCartsRepository):
    """SQLAlchemy-репозиторий корзины; позиции через selectinload."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: Cart) -> None:
        self._session.add(cart_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> Cart | None:
        result = await self._session.execute(
            select(CartModel)
            .where(CartModel.id == id_)
            .options(selectinload(CartModel.items))
        )
        model = result.scalar_one_or_none()
        return cart_to_entity(model) if model is not None else None

    async def update(self, entity: Cart) -> Cart:
        result = await self._session.execute(
            select(CartModel)
            .where(CartModel.id == entity.id)
            .options(selectinload(CartModel.items))
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Cart not found: {entity.id}")
        apply_cart(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(CartModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Cart | None:
        result = await self._session.execute(
            select(CartModel)
            .where(CartModel.user_id == user_id)
            .options(selectinload(CartModel.items))
        )
        model = result.scalar_one_or_none()
        return cart_to_entity(model) if model is not None else None
