import uuid
from datetime import datetime, timedelta, timezone

from src.domain.entities.user_sessions import UserSession


class TestUserSession:
    def test_create_minimal(self):
        user_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        session = UserSession(
            user_id=user_id,
            refresh_token_hash="hash",
            expires_at=expires_at,
        )

        assert session.user_id == user_id
        assert session.refresh_token_hash == "hash"
        assert session.expires_at == expires_at
        assert session.revoked_at is None
        assert session.user_agent is None

    def test_create_with_optional_fields(self):
        revoked_at = datetime.now(timezone.utc)

        session = UserSession(
            user_id=uuid.uuid4(),
            refresh_token_hash="hash2",
            expires_at=revoked_at + timedelta(days=1),
            revoked_at=revoked_at,
            user_agent="Mozilla/5.0",
            ip_hash="ip-hash",
        )

        assert session.revoked_at == revoked_at
        assert session.user_agent == "Mozilla/5.0"
        assert session.ip_hash == "ip-hash"

    def test_base_entity_fields(self):
        session = UserSession(
            user_id=uuid.uuid4(),
            refresh_token_hash="h",
            expires_at=datetime.now(timezone.utc),
        )

        assert session.id is not None
        assert session.created_at.tzinfo is not None
        assert session.updated_at.tzinfo is not None
