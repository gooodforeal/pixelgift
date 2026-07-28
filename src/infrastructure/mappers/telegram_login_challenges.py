from src.domain.entities.telegram_login_challenges import (
    LoginChallengeStatus,
    TelegramLoginChallenge,
)
from src.domain.values.telegram_id import TelegramId
from src.infrastructure.models.telegram_login_challenges import (
    TelegramLoginChallengeModel,
)


def telegram_login_challenge_to_model(
    entity: TelegramLoginChallenge,
) -> TelegramLoginChallengeModel:
    return TelegramLoginChallengeModel(
        id=entity.id,
        code=entity.code,
        status=entity.status.value,
        telegram_id=(
            int(entity.telegram_id.value) if entity.telegram_id is not None else None
        ),
        user_id=entity.user_id,
        expires_at=entity.expires_at,
        completed_at=entity.completed_at,
        created_at=entity.created_at,
        client_ip_hash=entity.client_ip_hash,
    )


def telegram_login_challenge_to_entity(
    model: TelegramLoginChallengeModel,
) -> TelegramLoginChallenge:
    return TelegramLoginChallenge(
        id=model.id,
        code=model.code,
        status=LoginChallengeStatus(model.status),
        telegram_id=(
            TelegramId(str(model.telegram_id)) if model.telegram_id is not None else None
        ),
        user_id=model.user_id,
        expires_at=model.expires_at,
        completed_at=model.completed_at,
        created_at=model.created_at,
        updated_at=model.created_at,
        client_ip_hash=model.client_ip_hash,
    )


def apply_telegram_login_challenge(
    entity: TelegramLoginChallenge,
    model: TelegramLoginChallengeModel,
) -> None:
    model.code = entity.code
    model.status = entity.status.value
    model.telegram_id = (
        int(entity.telegram_id.value) if entity.telegram_id is not None else None
    )
    model.user_id = entity.user_id
    model.expires_at = entity.expires_at
    model.completed_at = entity.completed_at
    model.client_ip_hash = entity.client_ip_hash
