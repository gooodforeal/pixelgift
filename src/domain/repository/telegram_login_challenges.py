from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.telegram_login_challenges import TelegramLoginChallenge
from src.domain.repository.base import BaseRepository


class BaseTelegramLoginChallengesRepository(
    BaseRepository[TelegramLoginChallenge], ABC
):
    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[TelegramLoginChallenge]: ...
