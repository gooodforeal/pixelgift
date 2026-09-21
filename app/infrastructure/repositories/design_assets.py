import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.design_assets import DesignAsset
from app.domain.repository.design_assets import BaseDesignAssetsRepository
from app.infrastructure.mappers.design_assets import (
    apply_design_asset,
    design_asset_to_entity,
    design_asset_to_model,
)
from app.infrastructure.models.design_assets import DesignAssetModel


class SqlAlchemyDesignAssetsRepository(BaseDesignAssetsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: DesignAsset) -> None:
        self._session.add(design_asset_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> DesignAsset | None:
        model = await self._session.get(DesignAssetModel, id_)
        return design_asset_to_entity(model) if model is not None else None

    async def update(self, entity: DesignAsset) -> DesignAsset:
        model = await self._session.get(DesignAssetModel, entity.id)
        if model is None:
            raise ValueError(f"Design asset not found: {entity.id}")
        apply_design_asset(entity, model)
        await self._session.flush()
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        model = await self._session.get(DesignAssetModel, id_)
        if model is not None:
            await self._session.delete(model)
