from abc import ABC, abstractmethod
import uuid

from src.domain.entities.media_files import MediaFile
from src.domain.repository.base import BaseRepository


class BaseMediaFilesRepository(BaseRepository[MediaFile], ABC):
    @abstractmethod
    async def list_by_owner_id(self, owner_id: uuid.UUID) -> list[MediaFile]: ...
