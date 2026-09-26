from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from app.domain.repository.assistant_chat_messages import (
    BaseAssistantChatMessagesRepository,
)
from app.domain.repository.assistant_chat_threads import (
    BaseAssistantChatThreadsRepository,
)
from app.domain.repository.boxes import BaseBoxesRepository
from app.domain.repository.box_designs import BaseBoxDesignsRepository
from app.domain.repository.carts import BaseCartsRepository
from app.domain.repository.design_assets import BaseDesignAssetsRepository
from app.domain.repository.design_ratings import BaseDesignRatingsRepository
from app.domain.repository.media_files import BaseMediaFilesRepository
from app.domain.repository.orders import BaseOrdersRepository
from app.domain.repository.products import BaseProductsRepository
from app.domain.repository.promo_codes import BasePromoCodesRepository
from app.domain.repository.telegram_login_challenges import (
    BaseTelegramLoginChallengesRepository,
)
from app.domain.repository.notification_jobs import BaseNotificationJobsRepository
from app.domain.repository.support_tickets import BaseSupportTicketsRepository
from app.domain.repository.user_balance_logs import BaseUserBalanceLogsRepository
from app.domain.repository.user_balances import BaseUserBalancesRepository
from app.domain.repository.user_sessions import BaseUserSessionsRepository
from app.domain.repository.users import BaseUsersRepository


class BaseUnitOfWork(ABC):
    users: BaseUsersRepository
    boxes: BaseBoxesRepository
    box_designs: BaseBoxDesignsRepository
    design_assets: BaseDesignAssetsRepository
    design_ratings: BaseDesignRatingsRepository
    media_files: BaseMediaFilesRepository
    notification_jobs: BaseNotificationJobsRepository
    support_tickets: BaseSupportTicketsRepository
    assistant_chat_threads: BaseAssistantChatThreadsRepository
    assistant_chat_messages: BaseAssistantChatMessagesRepository
    telegram_login_challenges: BaseTelegramLoginChallengesRepository
    user_sessions: BaseUserSessionsRepository
    products: BaseProductsRepository
    promo_codes: BasePromoCodesRepository
    carts: BaseCartsRepository
    orders: BaseOrdersRepository
    user_balances: BaseUserBalancesRepository
    user_balance_logs: BaseUserBalanceLogsRepository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
