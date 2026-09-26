from app.domain.entities.products import Product, ProductKind
from app.infrastructure.models.products import ProductModel


def product_to_model(entity: Product) -> ProductModel:
    return ProductModel(
        id=entity.id,
        sku=entity.sku,
        name=entity.name,
        description=entity.description,
        image_urls=list(entity.image_urls),
        kind=entity.kind.value,
        unit_price=entity.unit_price,
        currency=entity.currency,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def product_to_entity(model: ProductModel) -> Product:
    urls = model.image_urls or []
    return Product(
        id=model.id,
        sku=model.sku,
        name=model.name,
        description=model.description,
        image_urls=list(urls) if isinstance(urls, list) else [],
        kind=ProductKind(model.kind),
        unit_price=model.unit_price,
        currency=model.currency,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_product(entity: Product, model: ProductModel) -> None:
    model.sku = entity.sku
    model.name = entity.name
    model.description = entity.description
    model.image_urls = list(entity.image_urls)
    model.kind = entity.kind.value
    model.unit_price = entity.unit_price
    model.currency = entity.currency
    model.is_active = entity.is_active
    model.updated_at = entity.updated_at
