from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status

from src.application.use_cases.queries import GetCurrentUserUseCase, GetUserAvatarUseCase
from src.domain.entities.users import User
from src.domain.exceptions.auth import UserInactiveError
from src.domain.exceptions.users import UserNotFoundError
from src.infrastructure.storage.s3_storage import S3ObjectStorage
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.presentation.deps.auth import get_current_user_id
from src.presentation.deps.common import get_storage


def get_current_user_uc() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(SqlAlchemyUnitOfWork())


def get_user_avatar_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetUserAvatarUseCase:
    return GetUserAvatarUseCase(SqlAlchemyUnitOfWork(), storage)


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
