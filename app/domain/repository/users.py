"""Контракт персистентности пользователей."""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.users import User
from app.domain.repository.base import BaseRepository


class BaseUsersRepository(BaseRepository[User], ABC):
    """CRUD пользователя и поиск по telegram_id."""

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]: ...
