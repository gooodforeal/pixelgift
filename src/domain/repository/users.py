from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.users import User
from src.domain.repository.base import BaseRepository


class BaseUsersRepository(BaseRepository[User], ABC):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]: ...
