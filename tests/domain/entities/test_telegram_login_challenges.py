import uuid
from datetime import datetime, timedelta, timezone

from src.domain.entities.telegram_login_challenges import (
    LoginChallengeStatus,
    TelegramLoginChallenge,
)
from src.domain.values.telegram_id import TelegramId


class TestTelegramLoginChallenge:
    def test_create_minimal(self):
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        challenge = TelegramLoginChallenge(
            code="login_abc123",
            status=LoginChallengeStatus.PENDING,
            expires_at=expires_at,
        )

        assert challenge.code == "login_abc123"
        assert challenge.status == LoginChallengeStatus.PENDING
        assert challenge.expires_at == expires_at
        assert challenge.telegram_id is None
        assert challenge.user_id is None

    def test_create_with_optional_fields(self):
        user_id = uuid.uuid4()
        completed_at = datetime.now(timezone.utc)

        challenge = TelegramLoginChallenge(
            code="login_done",
            status=LoginChallengeStatus.COMPLETED,
            expires_at=completed_at + timedelta(minutes=5),
            telegram_id=TelegramId("999"),
            user_id=user_id,
            completed_at=completed_at,
            client_ip_hash="hash",
        )

        assert challenge.telegram_id is not None
        assert challenge.telegram_id.value == "999"
        assert challenge.user_id == user_id
        assert challenge.status == LoginChallengeStatus.COMPLETED
        assert challenge.client_ip_hash == "hash"

    def test_base_entity_fields(self):
        challenge = TelegramLoginChallenge(
            code="c",
            status=LoginChallengeStatus.EXPIRED,
            expires_at=datetime.now(timezone.utc),
        )

        assert challenge.id is not None
        assert challenge.created_at.tzinfo is not None
        assert challenge.updated_at.tzinfo is not None
