from app.domain.entities.box_designs import BoxDesign
from app.domain.values.box_design_description import BoxDesignDescription
from app.domain.values.box_design_name import BoxDesignName
from app.domain.values.sort_order import SortOrder
from app.domain.values.url import Url
from app.infrastructure.models.box_designs import BoxDesignModel


def box_design_to_model(entity: BoxDesign) -> BoxDesignModel:
    return BoxDesignModel(
        id=entity.id,
        code=entity.code,
        name=entity.name.value,
        description=(
            entity.description.value if entity.description is not None else None
        ),
        preview_image_url=entity.preview_image_url.value,
        preview_asset_id=entity.preview_asset_id,
        preview_asset_id_light=entity.preview_asset_id_light,
        theme_config=dict(entity.theme_config),
        is_active=entity.is_active,
        sort_order=entity.sort_order.value,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def box_design_to_entity(model: BoxDesignModel) -> BoxDesign:
    return BoxDesign(
        id=model.id,
        code=model.code,
        name=BoxDesignName(model.name),
        description=(
            BoxDesignDescription(model.description)
            if model.description is not None
            else None
        ),
        preview_image_url=Url(model.preview_image_url),
        preview_asset_id=model.preview_asset_id,
        preview_asset_id_light=model.preview_asset_id_light,
        theme_config=dict(model.theme_config or {}),
        is_active=model.is_active,
        sort_order=SortOrder(model.sort_order),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_box_design(entity: BoxDesign, model: BoxDesignModel) -> None:
    model.code = entity.code
    model.name = entity.name.value
    model.description = (
        entity.description.value if entity.description is not None else None
    )
    model.preview_image_url = entity.preview_image_url.value
    model.preview_asset_id = entity.preview_asset_id
    model.preview_asset_id_light = entity.preview_asset_id_light
    model.theme_config = dict(entity.theme_config)
    model.is_active = entity.is_active
    model.sort_order = entity.sort_order.value
    model.updated_at = entity.updated_at
