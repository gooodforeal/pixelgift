from datetime import datetime, timezone
from typing import Any
import re
import uuid

from src.application.dto.designs import BoxDesignWithRating, DesignRatingResult
from src.application.dto.media import MediaContent
from src.application.ports.storage.base import BaseObjectStorage
from src.application.uow.base import BaseUnitOfWork
from src.domain.entities.box_designs import BoxDesign
from src.domain.entities.design_assets import DesignAsset
from src.domain.entities.design_ratings import DesignRating
from src.domain.exceptions.box_designs import (
    BoxDesignCodeConflictError,
    BoxDesignNotFoundError,
    DesignAssetNotFoundError,
)
from src.domain.exceptions.boxes import BoxDesignNotAvailableError
from src.domain.exceptions.design_ratings import DesignAlreadyRatedError
from src.domain.exceptions.media_files import UnsupportedMediaTypeError
from src.domain.values.box_design_description import BoxDesignDescription
from src.domain.values.box_design_name import BoxDesignName
from src.domain.values.rating_stars import RatingStars
from src.domain.values.sort_order import SortOrder
from src.domain.values.url import Url

_IMAGE_MIMES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

_CODE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ListBoxDesignsUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        user_id: uuid.UUID | None = None,
    ) -> list[BoxDesignWithRating]:
        async with self._uow as uow:
            designs = await uow.box_designs.list_active()
            design_ids = [design.id for design in designs]
            aggregates = {
                item.design_id: item
                for item in await uow.design_ratings.list_aggregates_by_design_ids(
                    design_ids
                )
            }
            my_ratings: dict[uuid.UUID, int] = {}
            if user_id is not None:
                ratings = await uow.design_ratings.list_user_ratings_for_designs(
                    user_id=user_id,
                    design_ids=design_ids,
                )
                my_ratings = {
                    rating.design_id: rating.stars.value for rating in ratings
                }

            return [
                BoxDesignWithRating(
                    design=design,
                    rating_avg=(
                        round(aggregates[design.id].average, 2)
                        if design.id in aggregates
                        else 0.0
                    ),
                    rating_count=(
                        aggregates[design.id].count if design.id in aggregates else 0
                    ),
                    my_rating=my_ratings.get(design.id),
                )
                for design in designs
            ]


class RateDesignUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        user_id: uuid.UUID,
        design_id: uuid.UUID,
        stars: int,
    ) -> DesignRatingResult:
        rating_stars = RatingStars(stars)
        async with self._uow as uow:
            design = await uow.box_designs.get_by_id(design_id)
            if design is None or not design.is_active:
                raise BoxDesignNotAvailableError(design_id)

            existing = await uow.design_ratings.get_by_user_and_design(
                user_id=user_id,
                design_id=design_id,
            )
            if existing is not None:
                raise DesignAlreadyRatedError(design_id=design_id, user_id=user_id)

            now = datetime.now(timezone.utc)
            rating = DesignRating(
                user_id=user_id,
                design_id=design_id,
                stars=rating_stars,
                created_at=now,
                updated_at=now,
            )
            await uow.design_ratings.add(rating)
            await uow.commit()

            aggregates = await uow.design_ratings.list_aggregates_by_design_ids(
                [design_id]
            )
            aggregate = aggregates[0] if aggregates else None
            return DesignRatingResult(
                design_id=design_id,
                stars=rating_stars.value,
                rating_avg=round(aggregate.average, 2) if aggregate else 0.0,
                rating_count=aggregate.count if aggregate else 0,
            )


class ListAllBoxDesignsUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> list[BoxDesign]:
        async with self._uow as uow:
            return await uow.box_designs.list_all()


class GetBoxDesignUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, design_id: uuid.UUID) -> BoxDesign:
        async with self._uow as uow:
            design = await uow.box_designs.get_by_id(design_id)
            if design is None:
                raise BoxDesignNotFoundError(design_id)
            return design


class CreateBoxDesignUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        code: str,
        name: str,
        preview_image_url: str,
        description: str | None = None,
        theme_config: dict[str, Any] | None = None,
        is_active: bool = True,
        sort_order: int = 1,
    ) -> BoxDesign:
        normalized_code = _normalize_code(code)
        async with self._uow as uow:
            existing = await uow.box_designs.get_by_code(normalized_code)
            if existing is not None:
                raise BoxDesignCodeConflictError(normalized_code)

            now = datetime.now(timezone.utc)
            design = BoxDesign(
                code=normalized_code,
                name=BoxDesignName(name),
                preview_image_url=Url(preview_image_url),
                description=(
                    BoxDesignDescription(description)
                    if description is not None
                    else None
                ),
                theme_config=dict(theme_config or {}),
                is_active=is_active,
                sort_order=SortOrder(sort_order),
                created_at=now,
                updated_at=now,
            )
            await uow.box_designs.add(design)
            await uow.commit()
            return design


class UpdateBoxDesignUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        design_id: uuid.UUID,
        code: str | None = None,
        name: str | None = None,
        preview_image_url: str | None = None,
        description: str | None | object = ...,
        theme_config: dict[str, Any] | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> BoxDesign:
        async with self._uow as uow:
            design = await uow.box_designs.get_by_id(design_id)
            if design is None:
                raise BoxDesignNotFoundError(design_id)

            if code is not None:
                normalized_code = _normalize_code(code)
                if normalized_code != design.code:
                    existing = await uow.box_designs.get_by_code(normalized_code)
                    if existing is not None and existing.id != design.id:
                        raise BoxDesignCodeConflictError(normalized_code)
                    design.code = normalized_code

            if name is not None:
                design.name = BoxDesignName(name)
            if preview_image_url is not None:
                design.preview_image_url = Url(preview_image_url)
            if description is not ...:
                design.description = (
                    BoxDesignDescription(description)
                    if isinstance(description, str)
                    else None
                )
            if theme_config is not None:
                design.theme_config = dict(theme_config)
            if is_active is not None:
                design.is_active = is_active
            if sort_order is not None:
                design.sort_order = SortOrder(sort_order)

            design.updated_at = datetime.now(timezone.utc)
            await uow.box_designs.update(design)
            await uow.commit()
            return design


class UploadDesignAssetUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        storage: BaseObjectStorage,
        *,
        api_base_url: str,
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._api_base_url = api_base_url.rstrip("/")

    async def execute(
        self,
        *,
        data: bytes,
        content_type: str,
        original_filename: str | None = None,
    ) -> tuple[DesignAsset, str]:
        mime = (content_type or "").split(";", 1)[0].strip().lower()
        if mime not in _IMAGE_MIMES:
            # try extension fallback
            ext = _file_extension(original_filename)
            mime_from_ext = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
                ".gif": "image/gif",
            }.get(ext)
            if mime_from_ext is None:
                raise UnsupportedMediaTypeError(content_type, original_filename)
            mime = mime_from_ext

        asset_id = uuid.uuid4()
        extension = _IMAGE_MIMES[mime]
        storage_key = f"designs/{asset_id}{extension}"
        await self._storage.upload(storage_key, data, content_type=mime)

        now = datetime.now(timezone.utc)
        asset = DesignAsset(
            id=asset_id,
            storage_key=storage_key,
            mime_type=mime,
            size_bytes=len(data),
            original_filename=original_filename,
            created_at=now,
            updated_at=now,
        )
        async with self._uow as uow:
            await uow.design_assets.add(asset)
            await uow.commit()

        url = f"{self._api_base_url}/designs/assets/{asset.id}"
        return asset, url


class GetDesignAssetContentUseCase:
    def __init__(self, uow: BaseUnitOfWork, storage: BaseObjectStorage) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(self, *, asset_id: uuid.UUID) -> MediaContent:
        async with self._uow as uow:
            asset = await uow.design_assets.get_by_id(asset_id)
            if asset is None:
                raise DesignAssetNotFoundError(asset_id)

        data = await self._storage.download(asset.storage_key)
        return MediaContent(
            data=data,
            mime_type=asset.mime_type,
            filename=asset.original_filename,
        )


def _normalize_code(code: str) -> str:
    normalized = code.strip().lower()
    if not normalized or not _CODE_RE.match(normalized):
        raise ValueError(
            "Design code must be lowercase kebab-case (a-z, 0-9, hyphens)"
        )
    if len(normalized) > 10:
        raise ValueError("Design code is too long")
    return normalized


def _file_extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()
