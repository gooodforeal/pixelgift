import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.aggregates.boxes import Box
from src.domain.repository.boxes import BaseBoxesRepository
from src.domain.values.public_slug import PublicSlug
from src.infrastructure.mappers.boxes import (
    apply_box,
    apply_box_item,
    box_item_to_model,
    box_to_entity,
    box_to_model,
)
from src.infrastructure.models.boxes import BoxModel


class SqlAlchemyBoxesRepository(BaseBoxesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: Box) -> None:
        self._session.add(box_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> Box | None:
        result = await self._session.execute(
            select(BoxModel)
            .where(BoxModel.id == id_)
            .options(selectinload(BoxModel.items))
        )
        model = result.scalar_one_or_none()
        return box_to_entity(model) if model is not None else None

    async def update(self, entity: Box) -> Box:
        result = await self._session.execute(
            select(BoxModel)
            .where(BoxModel.id == entity.id)
            .options(selectinload(BoxModel.items))
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Box not found: {entity.id}")

        apply_box(entity, model)
        self._sync_items(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(BoxModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def get_by_public_slug(self, public_slug: PublicSlug) -> Box | None:
        result = await self._session.execute(
            select(BoxModel)
            .where(BoxModel.public_slug == public_slug.value)
            .options(selectinload(BoxModel.items))
        )
        model = result.scalar_one_or_none()
        return box_to_entity(model) if model is not None else None

    async def list_by_owner_id(self, owner_id: uuid.UUID) -> list[Box]:
        result = await self._session.execute(
            select(BoxModel)
            .where(BoxModel.owner_id == owner_id)
            .options(selectinload(BoxModel.items))
            .order_by(BoxModel.created_at.desc())
        )
        return [box_to_entity(model) for model in result.scalars().all()]

    def _sync_items(self, entity: Box, model: BoxModel) -> None:
        existing = {item.id: item for item in model.items}
        incoming_ids = {item.id for item in entity.items}

        for item_model in list(model.items):
            if item_model.id not in incoming_ids:
                model.items.remove(item_model)

        for item in entity.items:
            current = existing.get(item.id)
            if current is None:
                model.items.append(box_item_to_model(item))
            else:
                apply_box_item(item, current)
