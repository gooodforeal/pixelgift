from src.infrastructure.repositories.box_designs import SqlAlchemyBoxDesignsRepository
from src.infrastructure.repositories.boxes import SqlAlchemyBoxesRepository
from src.infrastructure.repositories.design_assets import SqlAlchemyDesignAssetsRepository
from src.infrastructure.repositories.design_ratings import SqlAlchemyDesignRatingsRepository
from src.infrastructure.repositories.media_files import SqlAlchemyMediaFilesRepository
from src.infrastructure.repositories.notification_jobs import (
    SqlAlchemyNotificationJobsRepository,
)
from src.infrastructure.repositories.support_tickets import (
    SqlAlchemySupportTicketsRepository,
)
from src.infrastructure.repositories.telegram_login_challenges import (
    SqlAlchemyTelegramLoginChallengesRepository,
)
from src.infrastructure.repositories.user_sessions import SqlAlchemyUserSessionsRepository
from src.infrastructure.repositories.users import SqlAlchemyUsersRepository

__all__ = [
    "SqlAlchemyBoxDesignsRepository",
    "SqlAlchemyBoxesRepository",
    "SqlAlchemyDesignAssetsRepository",
    "SqlAlchemyDesignRatingsRepository",
    "SqlAlchemyMediaFilesRepository",
    "SqlAlchemyNotificationJobsRepository",
    "SqlAlchemySupportTicketsRepository",
    "SqlAlchemyTelegramLoginChallengesRepository",
    "SqlAlchemyUserSessionsRepository",
    "SqlAlchemyUsersRepository",
]
