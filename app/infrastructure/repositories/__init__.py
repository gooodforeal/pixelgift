"""Экспорт SQLAlchemy-реализаций доменных репозиториев."""

from app.infrastructure.repositories.assistant_chat_messages import (
    SqlAlchemyAssistantChatMessagesRepository,
)
from app.infrastructure.repositories.assistant_chat_threads import (
    SqlAlchemyAssistantChatThreadsRepository,
)
from app.infrastructure.repositories.box_designs import SqlAlchemyBoxDesignsRepository
from app.infrastructure.repositories.boxes import SqlAlchemyBoxesRepository
from app.infrastructure.repositories.carts import SqlAlchemyCartsRepository
from app.infrastructure.repositories.design_assets import SqlAlchemyDesignAssetsRepository
from app.infrastructure.repositories.design_ratings import SqlAlchemyDesignRatingsRepository
from app.infrastructure.repositories.media_files import SqlAlchemyMediaFilesRepository
from app.infrastructure.repositories.notification_jobs import (
    SqlAlchemyNotificationJobsRepository,
)
from app.infrastructure.repositories.orders import SqlAlchemyOrdersRepository
from app.infrastructure.repositories.products import SqlAlchemyProductsRepository
from app.infrastructure.repositories.product_sales import (
    SqlAlchemyProductSalesRepository,
)
from app.infrastructure.repositories.promo_codes import SqlAlchemyPromoCodesRepository
from app.infrastructure.repositories.support_tickets import (
    SqlAlchemySupportTicketsRepository,
)
from app.infrastructure.repositories.telegram_login_challenges import (
    SqlAlchemyTelegramLoginChallengesRepository,
)
from app.infrastructure.repositories.user_balance_logs import (
    SqlAlchemyUserBalanceLogsRepository,
)
from app.infrastructure.repositories.user_balances import SqlAlchemyUserBalancesRepository
from app.infrastructure.repositories.user_sessions import SqlAlchemyUserSessionsRepository
from app.infrastructure.repositories.users import SqlAlchemyUsersRepository

__all__ = [
    "SqlAlchemyAssistantChatMessagesRepository",
    "SqlAlchemyAssistantChatThreadsRepository",
    "SqlAlchemyBoxDesignsRepository",
    "SqlAlchemyBoxesRepository",
    "SqlAlchemyCartsRepository",
    "SqlAlchemyDesignAssetsRepository",
    "SqlAlchemyDesignRatingsRepository",
    "SqlAlchemyMediaFilesRepository",
    "SqlAlchemyNotificationJobsRepository",
    "SqlAlchemyOrdersRepository",
    "SqlAlchemyProductsRepository",
    "SqlAlchemyProductSalesRepository",
    "SqlAlchemyPromoCodesRepository",
    "SqlAlchemySupportTicketsRepository",
    "SqlAlchemyTelegramLoginChallengesRepository",
    "SqlAlchemyUserBalanceLogsRepository",
    "SqlAlchemyUserBalancesRepository",
    "SqlAlchemyUserSessionsRepository",
    "SqlAlchemyUsersRepository",
]
