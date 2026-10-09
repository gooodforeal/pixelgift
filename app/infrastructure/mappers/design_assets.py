"""Маппинг DesignAsset ↔ DesignAssetModel."""

from app.domain.entities.design_assets import DesignAsset
from app.infrastructure.models.design_assets import DesignAssetModel


def design_asset_to_model(entity: DesignAsset) -> DesignAssetModel:
    return DesignAssetModel(
        id=entity.id,
        storage_key=entity.storage_key,
        mime_type=entity.mime_type,
        size_bytes=entity.size_bytes,
        original_filename=entity.original_filename,
        created_at=entity.created_at,
    )


def design_asset_to_entity(model: DesignAssetModel) -> DesignAsset:
    return DesignAsset(
        id=model.id,
        storage_key=model.storage_key,
        mime_type=model.mime_type,
        size_bytes=model.size_bytes,
        original_filename=model.original_filename,
        created_at=model.created_at,
        updated_at=model.created_at,
    )


def apply_design_asset(entity: DesignAsset, model: DesignAssetModel) -> None:
    model.storage_key = entity.storage_key
    model.mime_type = entity.mime_type
    model.size_bytes = entity.size_bytes
    model.original_filename = entity.original_filename
