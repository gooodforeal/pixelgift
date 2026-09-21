from abc import ABC, abstractmethod
import uuid

from app.domain.entities.media_files import MediaFile
from app.domain.repository.base import BaseRepository


class BaseMediaFilesRepository(BaseRepository[MediaFile], ABC):
    @abstractmethod
    async def list_by_owner_id(self, owner_id: uuid.UUID) -> list[MediaFile]: ...
