from fastapi import APIRouter, Depends, Query, status

from app.application.dto.commerce import CreatePromoCodeCommand, ListPromoCodesCommand
from app.application.use_cases.commerce import (
    CreatePromoCodeUseCase,
    ListPromoCodesUseCase,
)
from app.domain.entities.promo_codes import PromoCode
from app.domain.entities.users import User
from app.presentation.deps.commerce import (
    get_create_promo_code_uc,
    get_list_promo_codes_uc,
)
from app.presentation.deps.users import require_admin
from app.presentation.schemas.commerce import (
    CreatePromoCodeRequest,
    PromoCodeResponse,
    PromoCodeSchema,
    PromoCodesPageSchema,
    PromoCodesResponse,
)

router = APIRouter(prefix="/admin/promo-codes", tags=["admin-promo-codes"])


def _promo_to_schema(promo: PromoCode) -> PromoCodeSchema:
    return PromoCodeSchema(
        id=promo.id,
        code=promo.code,
        discount_percent=promo.discount_percent,
        expires_at=promo.expires_at,
        usage_count=promo.usage_count,
        is_active=promo.is_active,
        created_at=promo.created_at,
    )


@router.get("", response_model=PromoCodesResponse)
async def list_promo_codes(
    _: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    uc: ListPromoCodesUseCase = Depends(get_list_promo_codes_uc),
) -> PromoCodesResponse:
    result = await uc.execute(
        ListPromoCodesCommand(page=page, page_size=page_size)
    )
    return PromoCodesResponse(
        message="ok",
        result=PromoCodesPageSchema(
            items=[_promo_to_schema(p) for p in result.items],
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
    promo = await uc.execute(
        CreatePromoCodeCommand(
            actor_id=admin.id,
            code=body.code,
            discount_percent=body.discount_percent,
            expires_at=body.expires_at,
        )
    )
    return PromoCodeResponse(message="ok", result=_promo_to_schema(promo))
