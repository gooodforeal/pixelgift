"""SQLAlchemy-репозиторий заказов."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.orders import Order
from app.domain.repository.orders import BaseOrdersRepository
from app.infrastructure.mappers.orders import apply_order, order_to_entity, order_to_model
from app.infrastructure.models.orders import OrderModel


class SqlAlchemyOrdersRepository(BaseOrdersRepository):
    """SQLAlchemy-репозиторий заказов; items eager-load; поиск по payment/idempotency."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: Order) -> None:
        self._session.add(order_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> Order | None:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.id == id_)
            .options(selectinload(OrderModel.items))
        )
        model = result.scalar_one_or_none()
        return order_to_entity(model) if model is not None else None

    async def update(self, entity: Order) -> Order:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.id == entity.id)
            .options(selectinload(OrderModel.items))
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Order not found: {entity.id}")
        apply_order(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(OrderModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_provider_payment_id(
        self, provider_payment_id: str
    ) -> Order | None:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.provider_payment_id == provider_payment_id)
            .options(selectinload(OrderModel.items))
        )
        model = result.scalar_one_or_none()
        return order_to_entity(model) if model is not None else None

    async def get_by_idempotency_key(self, idempotency_key: str) -> Order | None:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.idempotency_key == idempotency_key)
            .options(selectinload(OrderModel.items))
        )
        model = result.scalar_one_or_none()
        return order_to_entity(model) if model is not None else None

    async def list_pending_by_user_id(
        self, user_id: uuid.UUID, *, limit: int = 20
    ) -> list[Order]:
        result = await self._session.execute(
            select(OrderModel)
            .where(
                OrderModel.user_id == user_id,
                OrderModel.status == "pending",
            )
            .options(selectinload(OrderModel.items))
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
        )
        return [order_to_entity(m) for m in result.scalars().all()]

    async def list_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[Order]:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .options(selectinload(OrderModel.items))
            .order_by(OrderModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [order_to_entity(m) for m in result.scalars().all()]

    async def count_by_user_id(self, user_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(OrderModel)
            .where(OrderModel.user_id == user_id)
        )
        return int(result.scalar_one())
