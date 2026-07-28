from abc import ABC
from abc import abstractmethod
import uuid
from typing import List, TypeVar, Generic, Optional

from src.domain.entities.base import BaseEntity


T = TypeVar("T", bound=BaseEntity)

class BaseRepository(Generic[T], ABC):
    @abstractmethod
    def add(self, entity: T) -> None:
        ...

    @abstractmethod
    def get_by_id(self, id_: uuid.UUID) -> Optional[T]:
        ...

    @abstractmethod
    def update(self, entity: T) -> T:
        ...

    @abstractmethod
    def delete(self, id_: uuid.UUID) -> None:
        ...
