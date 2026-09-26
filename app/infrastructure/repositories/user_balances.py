import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user_balances import UserBalance
from app.domain.repository.user_balances import BaseUserBalancesRepository
from app.infrastructure.mappers.user_balances import (
    apply_user_balance,
    user_balance_to_entity,
    user_balance_to_model,
)
from app.infrastructure.models.user_balances import UserBalanceModel


class SqlAlchemyUserBalancesRepository(BaseUserBalancesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: UserBalance) -> None:
        self._session.add(user_balance_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> UserBalance | None:
        model = await self._session.get(UserBalanceModel, id_)
        return user_balance_to_entity(model) if model is not None else None

    async def update(self, entity: UserBalance) -> UserBalance:
        model = await self._session.get(UserBalanceModel, entity.id)
        if model is None:
            raise ValueError(f"UserBalance not found: {entity.id}")
        apply_user_balance(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(UserBalanceModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_user_and_product(
        self, *, user_id: uuid.UUID, product_id: uuid.UUID
    ) -> UserBalance | None:
        result = await self._session.execute(
            select(UserBalanceModel).where(
                UserBalanceModel.user_id == user_id,
                UserBalanceModel.product_id == product_id,
            )
        )
        model = result.scalar_one_or_none()
        return user_balance_to_entity(model) if model is not None else None

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[UserBalance]:
        result = await self._session.execute(
            select(UserBalanceModel).where(UserBalanceModel.user_id == user_id)
        )
        return [user_balance_to_entity(m) for m in result.scalars().all()]
