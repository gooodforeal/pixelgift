import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.users import User
from app.domain.repository.users import BaseUsersRepository
from app.infrastructure.mappers.users import apply_user, user_to_entity, user_to_model
from app.infrastructure.models.users import UserModel


class SqlAlchemyUsersRepository(BaseUsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: User) -> None:
        self._session.add(user_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> User | None:
        model = await self._session.get(UserModel, id_)
        return user_to_entity(model) if model is not None else None

    async def update(self, entity: User) -> User:
        model = await self._session.get(UserModel, entity.id)
        if model is None:
            raise ValueError(f"User not found: {entity.id}")
        apply_user(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(UserModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        model = result.scalar_one_or_none()
        return user_to_entity(model) if model is not None else None
