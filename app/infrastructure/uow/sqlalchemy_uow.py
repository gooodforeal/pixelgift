from collections.abc import Callable
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.uow.base import BaseUnitOfWork
from app.infrastructure.database import get_session_factory
from app.infrastructure.repositories import (
    SqlAlchemyAssistantChatMessagesRepository,
    SqlAlchemyAssistantChatThreadsRepository,
    SqlAlchemyBoxDesignsRepository,
    SqlAlchemyBoxesRepository,
    SqlAlchemyCartsRepository,
    SqlAlchemyDesignAssetsRepository,
    SqlAlchemyDesignRatingsRepository,
    SqlAlchemyMediaFilesRepository,
    SqlAlchemyNotificationJobsRepository,
    SqlAlchemyOrdersRepository,
    SqlAlchemyProductsRepository,
    SqlAlchemyProductSalesRepository,
    SqlAlchemyPromoCodesRepository,
    SqlAlchemySupportTicketsRepository,
    SqlAlchemyTelegramLoginChallengesRepository,
    SqlAlchemyUserBalanceLogsRepository,
    SqlAlchemyUserBalancesRepository,
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
        self.support_tickets = SqlAlchemySupportTicketsRepository(self._session)
        self.assistant_chat_threads = SqlAlchemyAssistantChatThreadsRepository(
            self._session
        )
        self.assistant_chat_messages = SqlAlchemyAssistantChatMessagesRepository(
            self._session
        )
        self.telegram_login_challenges = SqlAlchemyTelegramLoginChallengesRepository(
            self._session
        )
        self.user_sessions = SqlAlchemyUserSessionsRepository(self._session)
        self.products = SqlAlchemyProductsRepository(self._session)
        self.product_sales = SqlAlchemyProductSalesRepository(self._session)
        self.promo_codes = SqlAlchemyPromoCodesRepository(self._session)
        self.carts = SqlAlchemyCartsRepository(self._session)
        self.orders = SqlAlchemyOrdersRepository(self._session)
        self.user_balances = SqlAlchemyUserBalancesRepository(self._session)
        self.user_balance_logs = SqlAlchemyUserBalanceLogsRepository(self._session)
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
