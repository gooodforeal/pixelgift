from collections.abc import Callable
from functools import lru_cache
import uuid

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services.jwt import JwtService
from src.application.use_cases.auth import (
    CompleteTelegramLoginUseCase,
    LogoutUseCase,
    PollTelegramLoginStatusUseCase,
    RefreshAccessTokenUseCase,
    StartTelegramLoginUseCase,
)
from src.application.use_cases.boxes import (
    AddBoxItemUseCase,
    ArchiveBoxUseCase,
    CreateBoxUseCase,
    PublishBoxUseCase,
    RemoveBoxItemUseCase,
    ReorderBoxItemsUseCase,
    UnarchiveBoxUseCase,
    UpdateBoxItemUseCase,
    UpdateBoxUseCase,
)
from src.application.use_cases.designs import (
    CreateBoxDesignUseCase,
    GetBoxDesignUseCase,
    GetDesignAssetContentUseCase,
    ListAllBoxDesignsUseCase,
    ListBoxDesignsUseCase,
    RateDesignUseCase,
    UpdateBoxDesignUseCase,
    UploadDesignAssetUseCase,
)
from src.application.use_cases.media import (
    GetOwnMediaContentUseCase,
    UploadMediaUseCase,
)
from src.application.use_cases.queries import (
    GetBoxUseCase,
    GetCurrentUserUseCase,
    GetPublicBoxItemContentUseCase,
    GetPublicBoxUseCase,
    GetUserAvatarUseCase,
    ListBoxesUseCase,
)
from src.domain.exceptions.auth import UserInactiveError
from src.domain.exceptions.users import UserNotFoundError
from src.domain.entities.users import User
from src.infrastructure.storage.s3_storage import S3ObjectStorage
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.infrastructure.worker.task_queue import TaskiqTaskQueue
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
    cfg: Settings = Depends(get_settings),
) -> PollTelegramLoginStatusUseCase:
    return PollTelegramLoginStatusUseCase(SqlAlchemyUnitOfWork(), jwt_service, cfg)


def get_refresh_access_token_uc(
    jwt_service: JwtService = Depends(get_jwt_service),
    cfg: Settings = Depends(get_settings),
) -> RefreshAccessTokenUseCase:
    return RefreshAccessTokenUseCase(SqlAlchemyUnitOfWork(), jwt_service, cfg)


def get_logout_uc() -> LogoutUseCase:
    return LogoutUseCase(SqlAlchemyUnitOfWork())


def get_complete_telegram_login_uc(
    storage: S3ObjectStorage = Depends(get_storage),
    cfg: Settings = Depends(get_settings),
) -> CompleteTelegramLoginUseCase:
    return CompleteTelegramLoginUseCase(
        SqlAlchemyUnitOfWork(),
        storage,
        api_base_url=cfg.api_base_url,
    )


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


def get_publish_box_uc() -> PublishBoxUseCase:
    return PublishBoxUseCase(SqlAlchemyUnitOfWork())


def get_archive_box_uc() -> ArchiveBoxUseCase:
    return ArchiveBoxUseCase(SqlAlchemyUnitOfWork())


def get_unarchive_box_uc() -> UnarchiveBoxUseCase:
    return UnarchiveBoxUseCase(SqlAlchemyUnitOfWork())


def get_list_designs_uc() -> ListBoxDesignsUseCase:
    return ListBoxDesignsUseCase(SqlAlchemyUnitOfWork())


def get_rate_design_uc() -> RateDesignUseCase:
    return RateDesignUseCase(SqlAlchemyUnitOfWork())


def get_list_all_designs_uc() -> ListAllBoxDesignsUseCase:
    return ListAllBoxDesignsUseCase(SqlAlchemyUnitOfWork())


def get_get_design_uc() -> GetBoxDesignUseCase:
    return GetBoxDesignUseCase(SqlAlchemyUnitOfWork())


def get_create_design_uc() -> CreateBoxDesignUseCase:
    return CreateBoxDesignUseCase(SqlAlchemyUnitOfWork())


def get_update_design_uc() -> UpdateBoxDesignUseCase:
    return UpdateBoxDesignUseCase(SqlAlchemyUnitOfWork())


def get_upload_design_asset_uc(
    storage: S3ObjectStorage = Depends(get_storage),
    cfg: Settings = Depends(get_settings),
) -> UploadDesignAssetUseCase:
    return UploadDesignAssetUseCase(
        SqlAlchemyUnitOfWork(),
        storage,
        api_base_url=cfg.api_base_url,
    )


def get_design_asset_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetDesignAssetContentUseCase:
    return GetDesignAssetContentUseCase(SqlAlchemyUnitOfWork(), storage)


def get_list_boxes_uc() -> ListBoxesUseCase:
    return ListBoxesUseCase(SqlAlchemyUnitOfWork())


def get_get_box_uc() -> GetBoxUseCase:
    return GetBoxUseCase(SqlAlchemyUnitOfWork())


def get_current_user_uc() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(SqlAlchemyUnitOfWork())


def get_user_avatar_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetUserAvatarUseCase:
    return GetUserAvatarUseCase(SqlAlchemyUnitOfWork(), storage)


def get_task_queue() -> TaskiqTaskQueue:
    return TaskiqTaskQueue()


def get_public_box_uc(
    storage: S3ObjectStorage = Depends(get_storage),
    task_queue: TaskiqTaskQueue = Depends(get_task_queue),
) -> GetPublicBoxUseCase:
    return GetPublicBoxUseCase(SqlAlchemyUnitOfWork(), storage, task_queue)


def get_upload_media_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> UploadMediaUseCase:
    return UploadMediaUseCase(SqlAlchemyUnitOfWork(), storage)


def get_own_media_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetOwnMediaContentUseCase:
    return GetOwnMediaContentUseCase(SqlAlchemyUnitOfWork(), storage)


def get_public_box_item_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetPublicBoxItemContentUseCase:
    return GetPublicBoxItemContentUseCase(SqlAlchemyUnitOfWork(), storage)


def _decode_user_id(jwt_service: JwtService, raw_token: str | None) -> uuid.UUID:
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = jwt_service.decode_access_token(raw_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    return payload.user_id


async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    jwt_service: JwtService = Depends(get_jwt_service),
    cfg: Settings = Depends(get_settings),
) -> uuid.UUID:
    raw: str | None = None
    if credentials is not None and credentials.scheme.lower() == "bearer":
        raw = credentials.credentials
    if not raw:
        raw = request.cookies.get(cfg.access_cookie_name)
    return _decode_user_id(jwt_service, raw)


async def get_optional_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    jwt_service: JwtService = Depends(get_jwt_service),
    cfg: Settings = Depends(get_settings),
) -> uuid.UUID | None:
    raw: str | None = None
    if credentials is not None and credentials.scheme.lower() == "bearer":
        raw = credentials.credentials
    if not raw:
        raw = request.cookies.get(cfg.access_cookie_name)
    if not raw:
        return None
    try:
        return _decode_user_id(jwt_service, raw)
    except HTTPException:
        return None


async def require_admin(
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: GetCurrentUserUseCase = Depends(get_current_user_uc),
) -> User:
    try:
        user = await uc.execute(user_id=user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except UserInactiveError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


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
