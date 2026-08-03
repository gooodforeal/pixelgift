from datetime import datetime, timezone
from typing import Any
import re
import uuid

from src.application.dto.media import MediaContent
from src.application.ports.storage.base import BaseObjectStorage
from src.application.uow.base import BaseUnitOfWork
from src.domain.entities.box_designs import BoxDesign
from src.domain.entities.design_assets import DesignAsset
from src.domain.exceptions.box_designs import (
    BoxDesignCodeConflictError,
    BoxDesignNotFoundError,
    DesignAssetNotFoundError,
)
from src.domain.exceptions.media_files import UnsupportedMediaTypeError
from src.domain.values.box_design_description import BoxDesignDescription
from src.domain.values.box_design_name import BoxDesignName
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

    async def execute(self) -> list[BoxDesign]:
        async with self._uow as uow:
            return await uow.box_designs.list_active()


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
