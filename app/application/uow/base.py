"""Абстракция unit of work для use case'ов application-слоя."""

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
from app.domain.repository.product_sales import BaseProductSalesRepository
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
    """Контракт единицы работы: один транзакционный контекст и репозитории домена.

    Реализация (адаптер инфраструктуры) открывает сессию БД, прокидывает репозитории
    в атрибуты и фиксирует или откатывает изменения через ``commit`` / ``rollback``.
    При выходе из ``async with`` при исключении вызывается ``rollback``.

    Attributes:
        users: Пользователи и профили.
        boxes: Подарочные боксы.
        box_designs: Темы оформления боксов.
        design_assets: Медиа-активы для дизайнов.
        design_ratings: Оценки дизайнов.
        media_files: Загруженные медиафайлы пользователей.
        notification_jobs: Отложенные задачи уведомлений.
        support_tickets: Обращения в поддержку.
        assistant_chat_threads: Потоки чата ассистента.
        assistant_chat_messages: Сообщения ассистента.
        telegram_login_challenges: Челленджи входа через Telegram.
        user_sessions: Сессии с refresh-токенами.
        products: Товары магазина.
        product_sales: Скидки на товары.
        promo_codes: Промокоды.
        carts: Корзины.
        orders: Заказы.
        user_balances: Балансы кредитов по товарам.
        user_balance_logs: Журнал операций с балансом.
    """

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
    product_sales: BaseProductSalesRepository
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
    async def commit(self) -> None:
        """Сохраняет накопленные изменения в хранилище."""

    @abstractmethod
    async def rollback(self) -> None:
        """Отменяет незафиксированные изменения в текущей транзакции."""
