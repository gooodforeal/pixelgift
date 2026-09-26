import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user_balance_logs import UserBalanceLog
from app.domain.repository.user_balance_logs import BaseUserBalanceLogsRepository
from app.infrastructure.mappers.user_balance_logs import (
    user_balance_log_to_entity,
    user_balance_log_to_model,
)
from app.infrastructure.models.user_balance_logs import UserBalanceLogModel


class SqlAlchemyUserBalanceLogsRepository(BaseUserBalanceLogsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: UserBalanceLog) -> None:
        self._session.add(user_balance_log_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> UserBalanceLog | None:
        model = await self._session.get(UserBalanceLogModel, id_)
        return user_balance_log_to_entity(model) if model is not None else None

    async def update(self, entity: UserBalanceLog) -> UserBalanceLog:
        raise NotImplementedError("UserBalanceLog is append-only")

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(UserBalanceLogModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_reason_reference(
        self,
        *,
        reason: str,
        reference_type: str,
        reference_id: uuid.UUID,
    ) -> UserBalanceLog | None:
        result = await self._session.execute(
            select(UserBalanceLogModel).where(
                UserBalanceLogModel.reason == reason,
                UserBalanceLogModel.reference_type == reference_type,
                UserBalanceLogModel.reference_id == reference_id,
            )
        )
        model = result.scalar_one_or_none()
        return user_balance_log_to_entity(model) if model is not None else None

    async def list_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[UserBalanceLog]:
        result = await self._session.execute(
            select(UserBalanceLogModel)
            .where(UserBalanceLogModel.user_id == user_id)
            .order_by(UserBalanceLogModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [user_balance_log_to_entity(m) for m in result.scalars().all()]

    async def count_by_user_id(self, user_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(UserBalanceLogModel)
            .where(UserBalanceLogModel.user_id == user_id)
        )
        return int(result.scalar_one())
