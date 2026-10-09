"""Админ-API товаров каталога."""

import uuid

from fastapi import APIRouter, Depends, status

from app.application.dto.commerce import CreateProductCommand, UpdateProductCommand
from app.application.use_cases.commerce import (
    CreateProductUseCase,
    ListAllProductsUseCase,
    UpdateProductUseCase,
)
from app.domain.entities.users import User
from app.presentation.deps.commerce import (
    get_create_product_uc,
    get_list_all_products_uc,
    get_update_product_uc,
)
from app.presentation.deps.users import require_admin
from app.presentation.schemas.commerce import (
    CreateProductRequest,
    ProductResponse,
    ProductsResponse,
    UpdateProductRequest,
)
from app.presentation.schemas.commerce_mappers import product_view_to_schema

router = APIRouter(prefix="/admin/products", tags=["admin-products"])


@router.get("", response_model=ProductsResponse)
async def list_all_products(
    _: User = Depends(require_admin),
    uc: ListAllProductsUseCase = Depends(get_list_all_products_uc),
) -> ProductsResponse:
    """GET /admin/products — все товары."""
    views = await uc.execute()
    return ProductsResponse(
        message="ok",
        result=[product_view_to_schema(v) for v in views],
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    body: CreateProductRequest,
    admin: User = Depends(require_admin),
    uc: CreateProductUseCase = Depends(get_create_product_uc),
) -> ProductResponse:
    """POST /admin/products — создание товара."""
    view = await uc.execute(
        CreateProductCommand(
            actor_id=admin.id,
            sku=body.sku,
            name=body.name,
            description=body.description,
            unit_price=body.unit_price,
            kind=body.kind,
            currency=body.currency,
            is_active=body.is_active,
            image_urls=body.image_urls,
            sale_discount_percent=body.sale_discount_percent,
        )
    )
    return ProductResponse(message="ok", result=product_view_to_schema(view))


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    body: UpdateProductRequest,
    admin: User = Depends(require_admin),
    uc: UpdateProductUseCase = Depends(get_update_product_uc),
) -> ProductResponse:
    """PATCH /admin/products/{product_id} — обновление товара."""
    update_sale = "sale_discount_percent" in body.model_fields_set
    view = await uc.execute(
        UpdateProductCommand(
            actor_id=admin.id,
            product_id=product_id,
            name=body.name,
            description=body.description,
            unit_price=body.unit_price,
            is_active=body.is_active,
            image_urls=body.image_urls,
            sale_discount_percent=body.sale_discount_percent,
            update_sale=update_sale,
        )
    )
    return ProductResponse(message="ok", result=product_view_to_schema(view))
