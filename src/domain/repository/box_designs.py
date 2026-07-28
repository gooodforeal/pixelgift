from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.box_designs import BoxDesign
from src.domain.repository.base import BaseRepository


class BaseBoxDesignsRepository(BaseRepository[BoxDesign], ABC):
    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[BoxDesign]: ...
