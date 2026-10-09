"""SQLAlchemy-репозиторий рейтингов дизайнов."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.design_ratings import DesignRating
from app.domain.repository.design_ratings import (
    BaseDesignRatingsRepository,
    DesignRatingAggregate,
)
from app.infrastructure.mappers.design_ratings import (
    apply_design_rating,
    design_rating_to_entity,
    design_rating_to_model,
)
from app.infrastructure.models.design_ratings import DesignRatingModel


class SqlAlchemyDesignRatingsRepository(BaseDesignRatingsRepository):
    """SQLAlchemy-репозиторий оценок; агрегаты avg/count по design_id."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: DesignRating) -> None:
        self._session.add(design_rating_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> DesignRating | None:
        model = await self._session.get(DesignRatingModel, id_)
        return design_rating_to_entity(model) if model is not None else None

    async def update(self, entity: DesignRating) -> DesignRating:
        model = await self._session.get(DesignRatingModel, entity.id)
        if model is None:
            raise ValueError(f"Design rating not found: {entity.id}")
        apply_design_rating(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(DesignRatingModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_user_and_design(
        self,
        *,
        user_id: uuid.UUID,
        design_id: uuid.UUID,
    ) -> DesignRating | None:
        result = await self._session.execute(
            select(DesignRatingModel).where(
                DesignRatingModel.user_id == user_id,
                DesignRatingModel.design_id == design_id,
            )
        )
        model = result.scalar_one_or_none()
        return design_rating_to_entity(model) if model is not None else None

    async def list_aggregates_by_design_ids(
        self,
        design_ids: list[uuid.UUID],
    ) -> list[DesignRatingAggregate]:
        if not design_ids:
            return []

        result = await self._session.execute(
            select(
                DesignRatingModel.design_id,
                func.avg(DesignRatingModel.stars),
                func.count(DesignRatingModel.id),
            )
            .where(DesignRatingModel.design_id.in_(design_ids))
            .group_by(DesignRatingModel.design_id)
        )
        aggregates: list[DesignRatingAggregate] = []
        for design_id, average, count in result.all():
            aggregates.append(
                DesignRatingAggregate(
                    design_id=design_id,
                    average=float(average) if average is not None else 0.0,
                    count=int(count),
                )
            )
        return aggregates

    async def list_user_ratings_for_designs(
        self,
        *,
        user_id: uuid.UUID,
        design_ids: list[uuid.UUID],
    ) -> list[DesignRating]:
        if not design_ids:
            return []

        result = await self._session.execute(
            select(DesignRatingModel).where(
                DesignRatingModel.user_id == user_id,
                DesignRatingModel.design_id.in_(design_ids),
            )
        )
        return [design_rating_to_entity(model) for model in result.scalars().all()]
