"""SQLAlchemy-репозиторий дизайнов боксов."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.box_designs import BoxDesign
from app.domain.repository.box_designs import BaseBoxDesignsRepository
from app.infrastructure.mappers.box_designs import (
    apply_box_design,
    box_design_to_entity,
    box_design_to_model,
)
from app.infrastructure.models.box_designs import BoxDesignModel


class SqlAlchemyBoxDesignsRepository(BaseBoxDesignsRepository):
    """SQLAlchemy-репозиторий тем коробок; list_active по sort_order."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: BoxDesign) -> None:
        self._session.add(box_design_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> BoxDesign | None:
        model = await self._session.get(BoxDesignModel, id_)
        return box_design_to_entity(model) if model is not None else None

    async def update(self, entity: BoxDesign) -> BoxDesign:
        model = await self._session.get(BoxDesignModel, entity.id)
        if model is None:
            raise ValueError(f"Box design not found: {entity.id}")
        apply_box_design(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(BoxDesignModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_code(self, code: str) -> BoxDesign | None:
        result = await self._session.execute(
            select(BoxDesignModel).where(BoxDesignModel.code == code)
        )
        model = result.scalar_one_or_none()
        return box_design_to_entity(model) if model is not None else None

    async def list_active(self) -> list[BoxDesign]:
        result = await self._session.execute(
            select(BoxDesignModel)
            .where(BoxDesignModel.is_active.is_(True))
            .order_by(BoxDesignModel.sort_order, BoxDesignModel.name)
        )
        return [box_design_to_entity(model) for model in result.scalars().all()]

    async def list_all(self) -> list[BoxDesign]:
        result = await self._session.execute(
            select(BoxDesignModel).order_by(
                BoxDesignModel.sort_order,
                BoxDesignModel.name,
            )
        )
        return [box_design_to_entity(model) for model in result.scalars().all()]
