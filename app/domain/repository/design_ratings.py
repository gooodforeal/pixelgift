"""Контракт персистентности оценок дизайнов."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import uuid
from typing import Optional

from app.domain.entities.design_ratings import DesignRating
from app.domain.repository.base import BaseRepository


@dataclass(frozen=True, slots=True)
class DesignRatingAggregate:
    """Сводная средняя оценка и число голосов по design_id."""

    design_id: uuid.UUID
    average: float
    count: int


class BaseDesignRatingsRepository(BaseRepository[DesignRating], ABC):
    """Оценки пользователя, агрегаты и пакетные выборки."""

    @abstractmethod
    async def get_by_user_and_design(
        self,
        *,
        user_id: uuid.UUID,
        design_id: uuid.UUID,
    ) -> Optional[DesignRating]: ...

    @abstractmethod
    async def list_aggregates_by_design_ids(
        self,
        design_ids: list[uuid.UUID],
    ) -> list[DesignRatingAggregate]: ...

    @abstractmethod
    async def list_user_ratings_for_designs(
        self,
        *,
        user_id: uuid.UUID,
        design_ids: list[uuid.UUID],
    ) -> list[DesignRating]: ...
