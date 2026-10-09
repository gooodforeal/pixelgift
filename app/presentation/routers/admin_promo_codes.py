"""Админ-API промокодов."""

from fastapi import APIRouter, Depends, Query, status
import uuid

from app.application.dto.commerce import (
    CreatePromoCodeCommand,
    ListPromoCodesCommand,
    SetPromoCodeActiveCommand,
)
from app.application.use_cases.commerce import (
    CreatePromoCodeUseCase,
    ListPromoCodesUseCase,
    SetPromoCodeActiveUseCase,
)
from app.domain.entities.users import User
from app.presentation.deps.commerce import (
    get_create_promo_code_uc,
    get_list_promo_codes_uc,
    get_set_promo_code_active_uc,
)
from app.presentation.deps.users import require_admin
from app.presentation.schemas.commerce import (
    CreatePromoCodeRequest,
    PromoCodeResponse,
    PromoCodeSchema,
    PromoCodesPageSchema,
    PromoCodesResponse,
    SetPromoCodeActiveRequest,
)

router = APIRouter(prefix="/admin/promo-codes", tags=["admin-promo-codes"])


@router.get("", response_model=PromoCodesResponse)
async def list_promo_codes(
    _: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    uc: ListPromoCodesUseCase = Depends(get_list_promo_codes_uc),
) -> PromoCodesResponse:
    """GET /admin/promo-codes — список промокодов."""
    result = await uc.execute(
        ListPromoCodesCommand(page=page, page_size=page_size)
    )
    return PromoCodesResponse(
        message="ok",
        result=PromoCodesPageSchema(
            items=[
                PromoCodeSchema(
                    id=p.id,
                    code=p.code,
                    discount_percent=p.discount_percent,
                    expires_at=p.expires_at,
                    usage_count=p.usage_count,
                    max_usages=p.max_usages,
                    is_active=p.is_active,
                    status=p.resolve_status(),
                    created_at=p.created_at,
                )
                for p in result.items
            ],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
        ),
    )


@router.post(
    "",
    response_model=PromoCodeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_promo_code(
    body: CreatePromoCodeRequest,
    admin: User = Depends(require_admin),
    uc: CreatePromoCodeUseCase = Depends(get_create_promo_code_uc),
) -> PromoCodeResponse:
    """POST /admin/promo-codes — создание промокода."""
    promo = await uc.execute(
        CreatePromoCodeCommand(
            actor_id=admin.id,
            code=body.code,
            discount_percent=body.discount_percent,
            expires_at=body.expires_at,
            max_usages=body.max_usages,
        )
    )
    return PromoCodeResponse(
        message="ok",
        result=PromoCodeSchema(
            id=promo.id,
            code=promo.code,
            discount_percent=promo.discount_percent,
            expires_at=promo.expires_at,
            usage_count=promo.usage_count,
            max_usages=promo.max_usages,
            is_active=promo.is_active,
            status=promo.resolve_status(),
            created_at=promo.created_at,
        ),
    )


@router.patch("/{promo_id}", response_model=PromoCodeResponse)
async def set_promo_code_active(
    promo_id: uuid.UUID,
    body: SetPromoCodeActiveRequest,
    admin: User = Depends(require_admin),
    uc: SetPromoCodeActiveUseCase = Depends(get_set_promo_code_active_uc),
) -> PromoCodeResponse:
    """PATCH /admin/promo-codes/{promo_id} — активность промокода."""
    promo = await uc.execute(
        SetPromoCodeActiveCommand(
            actor_id=admin.id,
            promo_id=promo_id,
            is_active=body.is_active,
        )
    )
    return PromoCodeResponse(
        message="ok",
        result=PromoCodeSchema(
            id=promo.id,
            code=promo.code,
            discount_percent=promo.discount_percent,
            expires_at=promo.expires_at,
            usage_count=promo.usage_count,
            max_usages=promo.max_usages,
            is_active=promo.is_active,
            status=promo.resolve_status(),
            created_at=promo.created_at,
        ),
    )
