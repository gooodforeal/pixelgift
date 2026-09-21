from __future__ import annotations

from fastapi import Depends

from app.application.use_cases.media import (
    GetOwnMediaContentUseCase,
    UploadMediaUseCase,
)
from app.infrastructure.storage.s3_storage import S3ObjectStorage
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.presentation.deps.common import get_storage


def get_upload_media_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> UploadMediaUseCase:
    return UploadMediaUseCase(SqlAlchemyUnitOfWork(), storage)


def get_own_media_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetOwnMediaContentUseCase:
    return GetOwnMediaContentUseCase(SqlAlchemyUnitOfWork(), storage)
