from app.infrastructure.repositories.box_designs import SqlAlchemyBoxDesignsRepository
from app.infrastructure.repositories.boxes import SqlAlchemyBoxesRepository
from app.infrastructure.repositories.design_assets import SqlAlchemyDesignAssetsRepository
from app.infrastructure.repositories.design_ratings import SqlAlchemyDesignRatingsRepository
from app.infrastructure.repositories.media_files import SqlAlchemyMediaFilesRepository
from app.infrastructure.repositories.notification_jobs import (
    SqlAlchemyNotificationJobsRepository,
)
from app.infrastructure.repositories.support_tickets import (
    SqlAlchemySupportTicketsRepository,
)
from app.infrastructure.repositories.telegram_login_challenges import (
    SqlAlchemyTelegramLoginChallengesRepository,
)
from app.infrastructure.repositories.user_sessions import SqlAlchemyUserSessionsRepository
from app.infrastructure.repositories.users import SqlAlchemyUsersRepository

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
