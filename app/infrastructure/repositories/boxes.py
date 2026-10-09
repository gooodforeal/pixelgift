"""SQLAlchemy-репозиторий боксов."""
import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.aggregates.boxes import Box, BoxStatus
from app.domain.repository.boxes import BaseBoxesRepository
from app.domain.values.public_slug import PublicSlug
from app.infrastructure.mappers.boxes import (
    apply_box,
    apply_box_item,
    box_item_to_model,
    box_to_entity,
    box_to_model,
)
from app.infrastructure.models.boxes import BoxModel


class SqlAlchemyBoxesRepository(BaseBoxesRepository):
    """SQLAlchemy-репозиторий коробок; items через selectinload; claim с SKIP LOCKED."""

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

    async def list_by_owner_id(
        self,
        owner_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Box]:
        stmt = (
            select(BoxModel)
            .where(BoxModel.owner_id == owner_id)
            .options(selectinload(BoxModel.items))
            .order_by(BoxModel.created_at.desc())
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        return [box_to_entity(model) for model in result.scalars().all()]

    async def count_by_owner_id(self, owner_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(BoxModel)
            .where(BoxModel.owner_id == owner_id)
        )
        return int(result.scalar_one())

    async def count_statuses_by_owner_id(
        self,
        owner_id: uuid.UUID,
    ) -> dict[str, int]:
        result = await self._session.execute(
            select(BoxModel.status, func.count())
            .where(BoxModel.owner_id == owner_id)
            .group_by(BoxModel.status)
        )
        return {str(status): int(count) for status, count in result.all()}

    async def count_opened_between(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> int:
        return await self._session.scalar(
            select(func.count(BoxModel.id)).where(
                BoxModel.first_opened_at >= start,
                BoxModel.first_opened_at < end,
            )
        ) or 0

    async def claim_due_to_activate(
        self,
        now: datetime,
        *,
        limit: int = 50,
    ) -> list[Box]:
        result = await self._session.execute(
            select(BoxModel)
            .where(
                BoxModel.status == BoxStatus.SCHEDULED.value,
                BoxModel.activates_at <= now,
            )
            .order_by(BoxModel.activates_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
            .options(selectinload(BoxModel.items))
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
