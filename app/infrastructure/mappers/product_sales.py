from app.domain.entities.product_sales import ProductSale
from app.infrastructure.models.product_sales import ProductSaleModel


def product_sale_to_model(entity: ProductSale) -> ProductSaleModel:
    return ProductSaleModel(
        id=entity.id,
        product_id=entity.product_id,
        discount_percent=entity.discount_percent,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def apply_product_sale(entity: ProductSale, model: ProductSaleModel) -> None:
    model.product_id = entity.product_id
    model.discount_percent = entity.discount_percent
    model.is_active = entity.is_active
    model.updated_at = entity.updated_at


def product_sale_to_entity(model: ProductSaleModel) -> ProductSale:
    return ProductSale(
        id=model.id,
        product_id=model.product_id,
        discount_percent=model.discount_percent,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
