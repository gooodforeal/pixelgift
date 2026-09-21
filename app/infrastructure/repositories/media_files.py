import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.media_files import MediaFile
from app.domain.repository.media_files import BaseMediaFilesRepository
from app.infrastructure.mappers.media_files import (
    apply_media_file,
    media_file_to_entity,
    media_file_to_model,
)
from app.infrastructure.models.media_files import MediaFileModel


class SqlAlchemyMediaFilesRepository(BaseMediaFilesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: MediaFile) -> None:
        self._session.add(media_file_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> MediaFile | None:
        model = await self._session.get(MediaFileModel, id_)
        return media_file_to_entity(model) if model is not None else None

    async def update(self, entity: MediaFile) -> MediaFile:
        model = await self._session.get(MediaFileModel, entity.id)
        if model is None:
            raise ValueError(f"Media file not found: {entity.id}")
        apply_media_file(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(MediaFileModel, id_)
        if model is not None:
            await self._session.delete(model)

    async def list_by_owner_id(self, owner_id: uuid.UUID) -> list[MediaFile]:
        result = await self._session.execute(
            select(MediaFileModel)
            .where(MediaFileModel.owner_id == owner_id)
            .order_by(MediaFileModel.created_at.desc())
        )
        return [media_file_to_entity(model) for model in result.scalars().all()]
