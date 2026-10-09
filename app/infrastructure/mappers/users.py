"""Маппинг User ↔ UserModel."""

from app.domain.entities.users import User
from app.domain.values.telegram_id import TelegramId
from app.domain.values.url import Url
from app.infrastructure.models.users import UserModel


def user_to_model(entity: User) -> UserModel:
    return UserModel(
        id=entity.id,
        telegram_id=int(entity.telegram_id.value),
        username=entity.username,
        first_name=entity.first_name,
        last_name=entity.last_name,
        language_code=entity.language_code,
        photo_url=entity.photo_url.value if entity.photo_url is not None else None,
        is_active=entity.is_active,
        is_admin=entity.is_admin,
        notifications_enabled=entity.notifications_enabled,
        last_seen_at=entity.last_seen_at,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def user_to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        telegram_id=TelegramId(str(model.telegram_id)),
        username=model.username,
        first_name=model.first_name,
        last_name=model.last_name,
        language_code=model.language_code,
        photo_url=Url(model.photo_url) if model.photo_url is not None else None,
        is_active=model.is_active,
        is_admin=model.is_admin,
        notifications_enabled=model.notifications_enabled,
        last_seen_at=model.last_seen_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_user(entity: User, model: UserModel) -> None:
    model.telegram_id = int(entity.telegram_id.value)
    model.username = entity.username
    model.first_name = entity.first_name
    model.last_name = entity.last_name
    model.language_code = entity.language_code
    model.photo_url = entity.photo_url.value if entity.photo_url is not None else None
    model.is_active = entity.is_active
    model.is_admin = entity.is_admin
    model.notifications_enabled = entity.notifications_enabled
    model.last_seen_at = entity.last_seen_at
    model.updated_at = entity.updated_at
