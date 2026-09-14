from collections.abc import Callable
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.uow.base import BaseUnitOfWork
from src.infrastructure.database import get_session_factory
from src.infrastructure.repositories import (
    SqlAlchemyBoxDesignsRepository,
    SqlAlchemyBoxesRepository,
    SqlAlchemyDesignAssetsRepository,
    SqlAlchemyDesignRatingsRepository,
    SqlAlchemyMediaFilesRepository,
    SqlAlchemyNotificationJobsRepository,
    SqlAlchemyTelegramLoginChallengesRepository,
    SqlAlchemyUserSessionsRepository,
    SqlAlchemyUsersRepository,
)


class SqlAlchemyUnitOfWork(BaseUnitOfWork):
    def __init__(
        self,
        session_factory: Callable[[], AsyncSession] | None = None,
    ) -> None:
        self._session_factory = session_factory or get_session_factory()
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.users = SqlAlchemyUsersRepository(self._session)
        self.boxes = SqlAlchemyBoxesRepository(self._session)
        self.box_designs = SqlAlchemyBoxDesignsRepository(self._session)
        self.design_assets = SqlAlchemyDesignAssetsRepository(self._session)
        self.design_ratings = SqlAlchemyDesignRatingsRepository(self._session)
        self.media_files = SqlAlchemyMediaFilesRepository(self._session)
        self.notification_jobs = SqlAlchemyNotificationJobsRepository(self._session)
        self.telegram_login_challenges = SqlAlchemyTelegramLoginChallengesRepository(
            self._session
        )
        self.user_sessions = SqlAlchemyUserSessionsRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
