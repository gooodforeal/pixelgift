import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.application.use_cases.designs import (
    GetDesignAssetContentUseCase,
    ListBoxDesignsUseCase,
    RateDesignUseCase,
)
from app.domain.exceptions.box_designs import DesignAssetNotFoundError
from app.domain.exceptions.boxes import BoxDesignNotAvailableError
from app.domain.exceptions.design_ratings import (
    DesignAlreadyRatedError,
    DesignRatingStarsNotIntegerError,
    DesignRatingStarsOutOfRangeError,
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
    BoxDesignResponse,
    DesignRatingResponse,
    RateDesignRequest,
)
from app.presentation.schemas.mappers import box_design_with_rating_to_response

router = APIRouter(prefix="/designs", tags=["designs"])


@router.get("", response_model=list[BoxDesignResponse])
async def list_designs(
    uc: ListBoxDesignsUseCase = Depends(get_list_designs_uc),
    user_id: uuid.UUID | None = Depends(get_optional_current_user_id),
) -> list[BoxDesignResponse]:
    designs = await uc.execute(user_id=user_id)
    return [box_design_with_rating_to_response(item) for item in designs]


@router.get("/assets/{asset_id}")
async def get_design_asset(
    asset_id: uuid.UUID,
    uc: GetDesignAssetContentUseCase = Depends(get_design_asset_content_uc),
) -> Response:
    try:
        content = await uc.execute(asset_id=asset_id)
    except DesignAssetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

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
    try:
        result = await uc.execute(
            user_id=user_id,
            design_id=design_id,
            stars=body.stars,
        )
    except BoxDesignNotAvailableError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DesignAlreadyRatedError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (DesignRatingStarsOutOfRangeError, DesignRatingStarsNotIntegerError) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return DesignRatingResponse(
        design_id=result.design_id,
        stars=result.stars,
        rating_avg=result.rating_avg,
        rating_count=result.rating_count,
    )
