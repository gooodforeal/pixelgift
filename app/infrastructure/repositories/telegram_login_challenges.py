"""SQLAlchemy-репозиторий challenge Telegram-логина."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.telegram_login_challenges import TelegramLoginChallenge
from app.domain.repository.telegram_login_challenges import (
    BaseTelegramLoginChallengesRepository,
)
from app.infrastructure.mappers.telegram_login_challenges import (
    apply_telegram_login_challenge,
    telegram_login_challenge_to_entity,
    telegram_login_challenge_to_model,
)
from app.infrastructure.models.telegram_login_challenges import (
    TelegramLoginChallengeModel,
)


class SqlAlchemyTelegramLoginChallengesRepository(
    BaseTelegramLoginChallengesRepository
):
    """SQLAlchemy-репозиторий challenge входа; get_by_code с опциональным FOR UPDATE."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: TelegramLoginChallenge) -> None:
        self._session.add(telegram_login_challenge_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> TelegramLoginChallenge | None:
        model = await self._session.get(TelegramLoginChallengeModel, id_)
        return telegram_login_challenge_to_entity(model) if model is not None else None

    async def update(self, entity: TelegramLoginChallenge) -> TelegramLoginChallenge:
        model = await self._session.get(TelegramLoginChallengeModel, entity.id)
        if model is None:
            raise ValueError(f"Telegram login challenge not found: {entity.id}")
        apply_telegram_login_challenge(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(TelegramLoginChallengeModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_code(
        self, code: str, *, for_update: bool = False
    ) -> TelegramLoginChallenge | None:
        stmt = select(TelegramLoginChallengeModel).where(
            TelegramLoginChallengeModel.code == code
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return telegram_login_challenge_to_entity(model) if model is not None else None
