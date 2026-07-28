from collections.abc import Callable
from functools import lru_cache
import uuid

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services.jwt import JwtService
from src.application.use_cases.auth import (
    CompleteTelegramLoginUseCase,
    PollTelegramLoginStatusUseCase,
    StartTelegramLoginUseCase,
)
from src.application.use_cases.boxes import (
    AddBoxItemUseCase,
    CreateBoxUseCase,
    RemoveBoxItemUseCase,
    ReorderBoxItemsUseCase,
    UpdateBoxItemUseCase,
    UpdateBoxUseCase,
)
from src.application.use_cases.media import UploadMediaUseCase
from src.application.use_cases.queries import (
    GetBoxUseCase,
    GetPublicBoxUseCase,
    ListBoxesUseCase,
)
from src.infrastructure.storage.s3_storage import S3ObjectStorage
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.settings import Settings, settings

_bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_settings() -> Settings:
    return settings


def get_jwt_service(cfg: Settings = Depends(get_settings)) -> JwtService:
    return JwtService(cfg)


def get_storage(cfg: Settings = Depends(get_settings)) -> S3ObjectStorage:
    return S3ObjectStorage(
        endpoint_url=cfg.minio_endpoint,
        access_key=cfg.minio_access_key,
        secret_key=cfg.minio_secret_key,
        bucket=cfg.minio_bucket,
        region=cfg.minio_region,
    )


def uow_factory() -> Callable[[], SqlAlchemyUnitOfWork]:
    return SqlAlchemyUnitOfWork


def get_start_telegram_login_uc(
    cfg: Settings = Depends(get_settings),
) -> StartTelegramLoginUseCase:
    return StartTelegramLoginUseCase(SqlAlchemyUnitOfWork(), cfg)


def get_poll_telegram_login_uc(
    jwt_service: JwtService = Depends(get_jwt_service),
) -> PollTelegramLoginStatusUseCase:
    return PollTelegramLoginStatusUseCase(SqlAlchemyUnitOfWork(), jwt_service)


def get_complete_telegram_login_uc() -> CompleteTelegramLoginUseCase:
    return CompleteTelegramLoginUseCase(SqlAlchemyUnitOfWork())


def get_create_box_uc() -> CreateBoxUseCase:
    return CreateBoxUseCase(SqlAlchemyUnitOfWork())


def get_update_box_uc() -> UpdateBoxUseCase:
    return UpdateBoxUseCase(SqlAlchemyUnitOfWork())


def get_add_box_item_uc() -> AddBoxItemUseCase:
    return AddBoxItemUseCase(SqlAlchemyUnitOfWork())


def get_update_box_item_uc() -> UpdateBoxItemUseCase:
    return UpdateBoxItemUseCase(SqlAlchemyUnitOfWork())


def get_remove_box_item_uc() -> RemoveBoxItemUseCase:
    return RemoveBoxItemUseCase(SqlAlchemyUnitOfWork())


def get_reorder_box_items_uc() -> ReorderBoxItemsUseCase:
    return ReorderBoxItemsUseCase(SqlAlchemyUnitOfWork())


def get_list_boxes_uc() -> ListBoxesUseCase:
    return ListBoxesUseCase(SqlAlchemyUnitOfWork())


def get_get_box_uc() -> GetBoxUseCase:
    return GetBoxUseCase(SqlAlchemyUnitOfWork())


def get_public_box_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetPublicBoxUseCase:
    return GetPublicBoxUseCase(SqlAlchemyUnitOfWork(), storage)


def get_upload_media_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> UploadMediaUseCase:
    return UploadMediaUseCase(SqlAlchemyUnitOfWork(), storage)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> uuid.UUID:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = jwt_service.decode_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    return payload.user_id


async def verify_bot_api_secret(
    x_bot_api_secret: str | None = Header(default=None),
    cfg: Settings = Depends(get_settings),
) -> None:
    expected = cfg.bot_api_secret
    if not expected or x_bot_api_secret != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid bot API secret",
        )
