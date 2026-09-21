from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.telegram_login_challenges import TelegramLoginChallenge
from app.domain.repository.base import BaseRepository


class BaseTelegramLoginChallengesRepository(
    BaseRepository[TelegramLoginChallenge], ABC
):
    @abstractmethod
    async def get_by_code(
        self, code: str, *, for_update: bool = False
    ) -> Optional[TelegramLoginChallenge]: ...
