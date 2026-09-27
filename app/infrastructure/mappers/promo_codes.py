from app.domain.entities.promo_codes import PromoCode
from app.infrastructure.models.promo_codes import PromoCodeModel


def promo_code_to_model(entity: PromoCode) -> PromoCodeModel:
    return PromoCodeModel(
        id=entity.id,
        code=entity.code,
        discount_percent=entity.discount_percent,
        expires_at=entity.expires_at,
        usage_count=entity.usage_count,
        max_usages=entity.max_usages,
        is_active=entity.is_active,
        created_by_user_id=entity.created_by_user_id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def promo_code_to_entity(
    model: PromoCodeModel,
) -> PromoCode:
    return PromoCode(
        id=model.id,
        code=model.code,
        discount_percent=model.discount_percent,
        expires_at=model.expires_at,
        usage_count=model.usage_count,
        max_usages=model.max_usages,
        is_active=model.is_active,
        created_by_user_id=model.created_by_user_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_promo_code(entity: PromoCode, model: PromoCodeModel) -> None:
    model.code = entity.code
    model.discount_percent = entity.discount_percent
    model.expires_at = entity.expires_at
    model.usage_count = entity.usage_count
    model.max_usages = entity.max_usages
    model.is_active = entity.is_active
    model.created_by_user_id = entity.created_by_user_id
    model.updated_at = entity.updated_at
