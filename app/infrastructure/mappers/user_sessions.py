from app.domain.entities.user_sessions import UserSession
from app.infrastructure.models.user_sessions import UserSessionModel


def user_session_to_model(entity: UserSession) -> UserSessionModel:
    return UserSessionModel(
        id=entity.id,
        user_id=entity.user_id,
        refresh_token_hash=entity.refresh_token_hash,
        expires_at=entity.expires_at,
        revoked_at=entity.revoked_at,
        created_at=entity.created_at,
        user_agent=entity.user_agent,
        ip_hash=entity.ip_hash,
    )


def user_session_to_entity(model: UserSessionModel) -> UserSession:
    return UserSession(
        id=model.id,
        user_id=model.user_id,
        refresh_token_hash=model.refresh_token_hash,
        expires_at=model.expires_at,
        revoked_at=model.revoked_at,
        created_at=model.created_at,
        updated_at=model.created_at,
        user_agent=model.user_agent,
        ip_hash=model.ip_hash,
    )


def apply_user_session(entity: UserSession, model: UserSessionModel) -> None:
    model.user_id = entity.user_id
    model.refresh_token_hash = entity.refresh_token_hash
    model.expires_at = entity.expires_at
    model.revoked_at = entity.revoked_at
    model.user_agent = entity.user_agent
    model.ip_hash = entity.ip_hash
