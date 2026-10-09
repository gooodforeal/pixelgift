"""Контракт персистентности агрегата Box."""

from abc import ABC, abstractmethod
from datetime import datetime
import uuid

from app.domain.aggregates.boxes import Box
from app.domain.repository.base import BaseRepository
from app.domain.values.public_slug import PublicSlug


class BaseBoxesRepository(BaseRepository[Box], ABC):
    """Репозиторий агрегата Box (корень и вложенные items)."""

    @abstractmethod
    async def get_by_public_slug(self, public_slug: PublicSlug) -> Box | None: ...

    @abstractmethod
    async def list_by_owner_id(
        self,
        owner_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Box]: ...

    @abstractmethod
    async def count_by_owner_id(self, owner_id: uuid.UUID) -> int: ...

    @abstractmethod
    async def count_statuses_by_owner_id(
        self,
        owner_id: uuid.UUID,
    ) -> dict[str, int]: ...

    @abstractmethod
    async def count_opened_between(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> int: ...

    @abstractmethod
    async def claim_due_to_activate(
        self,
        now: datetime,
        *,
        limit: int = 50,
    ) -> list[Box]: ...
