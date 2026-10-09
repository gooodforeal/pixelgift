"""Зависимости профиля пользователя и проверки прав администратора."""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status

from app.application.use_cases.queries import GetCurrentUserUseCase, GetUserAvatarUseCase
from app.domain.entities.users import User
from app.domain.exceptions.auth import UserInactiveError
from app.domain.exceptions.users import UserNotFoundError
from app.infrastructure.storage.s3_storage import S3ObjectStorage
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.presentation.deps.auth import get_current_user_id
from app.presentation.deps.common import get_storage


def get_current_user_uc() -> GetCurrentUserUseCase:
    """Use case загрузки текущего пользователя по id."""
    return GetCurrentUserUseCase(SqlAlchemyUnitOfWork())


def get_user_avatar_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetUserAvatarUseCase:
    """Use case выдачи байтов аватара пользователя из хранилища."""
    return GetUserAvatarUseCase(SqlAlchemyUnitOfWork(), storage)


async def require_admin(
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: GetCurrentUserUseCase = Depends(get_current_user_uc),
) -> User:
    """Требует активного пользователя с флагом is_admin."""
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
