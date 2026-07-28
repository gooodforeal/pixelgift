from abc import ABC, abstractmethod
import uuid

from src.domain.aggregates.boxes import Box
from src.domain.repository.base import BaseRepository
from src.domain.values.public_slug import PublicSlug


class BaseBoxesRepository(BaseRepository[Box], ABC):
    """Repository for the Box aggregate (box root + nested items)."""

    @abstractmethod
    async def get_by_public_slug(self, public_slug: PublicSlug) -> Box | None: ...

    @abstractmethod
    async def list_by_owner_id(self, owner_id: uuid.UUID) -> list[Box]: ...
