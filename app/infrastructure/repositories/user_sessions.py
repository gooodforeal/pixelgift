import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user_sessions import UserSession
from app.domain.repository.user_sessions import BaseUserSessionsRepository
from app.infrastructure.mappers.user_sessions import (
    apply_user_session,
    user_session_to_entity,
    user_session_to_model,
)
from app.infrastructure.models.user_sessions import UserSessionModel


class SqlAlchemyUserSessionsRepository(BaseUserSessionsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: UserSession) -> None:
        self._session.add(user_session_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> UserSession | None:
        model = await self._session.get(UserSessionModel, id_)
        return user_session_to_entity(model) if model is not None else None

    async def update(self, entity: UserSession) -> UserSession:
        model = await self._session.get(UserSessionModel, entity.id)
        if model is None:
            raise ValueError(f"User session not found: {entity.id}")
        apply_user_session(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(UserSessionModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_refresh_token_hash(
        self, refresh_token_hash: str
    ) -> UserSession | None:
        result = await self._session.execute(
            select(UserSessionModel).where(
                UserSessionModel.refresh_token_hash == refresh_token_hash
            )
        )
        model = result.scalar_one_or_none()
        return user_session_to_entity(model) if model is not None else None

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[UserSession]:
        result = await self._session.execute(
            select(UserSessionModel).where(UserSessionModel.user_id == user_id)
        )
        return [user_session_to_entity(model) for model in result.scalars().all()]
