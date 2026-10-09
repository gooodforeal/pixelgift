"""Абстрактный контракт CRUD-репозитория для сущностей домена."""

from abc import ABC, abstractmethod
import uuid
from typing import Generic, Optional, TypeVar

from app.domain.entities.base import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(Generic[T], ABC):
    """Минимальный набор асинхронных операций персистентности сущности."""

    @abstractmethod
    async def add(self, entity: T) -> None: ...

    @abstractmethod
    async def get_by_id(self, id_: uuid.UUID) -> Optional[T]: ...

    @abstractmethod
    async def update(self, entity: T) -> T: ...

    @abstractmethod
    async def delete(self, id_: uuid.UUID) -> None: ...
