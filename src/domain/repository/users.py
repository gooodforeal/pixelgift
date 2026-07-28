from abc import ABC, abstractmethod
from typing import Optional

from src.domain.repository.base import BaseRepository
from src.domain.entities.users import User


class UsersRepository(BaseRepository[User], ABC):
    @abstractmethod
    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        ...