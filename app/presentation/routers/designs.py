"""Публичный каталог дизайнов боксов и оценки."""

import uuid

from fastapi import APIRouter, Depends, Response

from app.application.use_cases.designs import (
    GetDesignAssetContentUseCase,
    ListBoxDesignsUseCase,
    RateDesignUseCase,
)
from app.presentation.deps.auth import (
    get_current_user_id,
    get_optional_current_user_id,
)
from app.presentation.deps.designs import (
    get_design_asset_content_uc,
    get_list_designs_uc,
    get_rate_design_uc,
)
from app.presentation.schemas.designs import (
    BoxDesignListResponse,
    DesignRatingResponse,
    DesignRatingSchema,
    RateDesignRequest,
)
from app.presentation.schemas.mappers import box_design_with_rating_to_response

router = APIRouter(prefix="/designs", tags=["designs"])


@router.get("", response_model=BoxDesignListResponse)
async def list_designs(
    uc: ListBoxDesignsUseCase = Depends(get_list_designs_uc),
    user_id: uuid.UUID | None = Depends(get_optional_current_user_id),
) -> BoxDesignListResponse:
    """GET /designs — список активных дизайнов с рейтингом."""
    designs = await uc.execute(user_id=user_id)
    return BoxDesignListResponse(
        message="Success",
        result=[box_design_with_rating_to_response(item) for item in designs],
    )


@router.get("/assets/{asset_id}")
async def get_design_asset(
    asset_id: uuid.UUID,
    uc: GetDesignAssetContentUseCase = Depends(get_design_asset_content_uc),
) -> Response:
    """GET /designs/assets/{asset_id} — файл ассета."""
    content = await uc.execute(asset_id=asset_id)
    return Response(
        content=content.data,
        media_type=content.mime_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.put("/{design_id}/rating", response_model=DesignRatingResponse)
async def rate_design(
    design_id: uuid.UUID,
    body: RateDesignRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: RateDesignUseCase = Depends(get_rate_design_uc),
) -> DesignRatingResponse:
    """PUT /designs/{design_id}/rating — оценка 1–5 звёзд."""
    result = await uc.execute(
        user_id=user_id,
        design_id=design_id,
        stars=body.stars,
    )
    return DesignRatingResponse(
        message="Success",
        result=DesignRatingSchema(
            design_id=result.design_id,
            stars=result.stars,
            rating_avg=result.rating_avg,
            rating_count=result.rating_count,
        ),
    )
