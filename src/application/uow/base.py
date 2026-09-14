from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from src.domain.repository.boxes import BaseBoxesRepository
from src.domain.repository.box_designs import BaseBoxDesignsRepository
from src.domain.repository.design_assets import BaseDesignAssetsRepository
from src.domain.repository.design_ratings import BaseDesignRatingsRepository
from src.domain.repository.media_files import BaseMediaFilesRepository
from src.domain.repository.telegram_login_challenges import (
    BaseTelegramLoginChallengesRepository,
)
from src.domain.repository.notification_jobs import BaseNotificationJobsRepository
from src.domain.repository.user_sessions import BaseUserSessionsRepository
from src.domain.repository.users import BaseUsersRepository


class BaseUnitOfWork(ABC):
    users: BaseUsersRepository
    boxes: BaseBoxesRepository
    box_designs: BaseBoxDesignsRepository
    design_assets: BaseDesignAssetsRepository
    design_ratings: BaseDesignRatingsRepository
    media_files: BaseMediaFilesRepository
    notification_jobs: BaseNotificationJobsRepository
    telegram_login_challenges: BaseTelegramLoginChallengesRepository
    user_sessions: BaseUserSessionsRepository

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
