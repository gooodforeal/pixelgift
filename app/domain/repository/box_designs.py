"""Контракт персистентности дизайнов боксов."""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.box_designs import BoxDesign
from app.domain.repository.base import BaseRepository


class BaseBoxDesignsRepository(BaseRepository[BoxDesign], ABC):
    """Дизайны по code и списки active/all."""

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[BoxDesign]: ...

    @abstractmethod
    async def list_active(self) -> list[BoxDesign]: ...

    @abstractmethod
    async def list_all(self) -> list[BoxDesign]: ...
