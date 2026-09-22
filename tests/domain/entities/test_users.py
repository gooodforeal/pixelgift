from datetime import datetime, timezone

from app.domain.entities.users import User
from app.domain.values.telegram_id import TelegramId
from app.domain.values.url import Url


class TestUser:
    def test_create_minimal(self):
        user = User(telegram_id=TelegramId("123456789"), first_name="Alice")

        assert user.telegram_id.value == "123456789"
        assert user.first_name == "Alice"
        assert user.username is None
        assert user.is_active is True
        assert user.is_admin is False
        assert user.notifications_enabled is True

    def test_create_with_optional_fields(self):
        seen = datetime(2026, 1, 1, tzinfo=timezone.utc)
        user = User(
            telegram_id=TelegramId("42"),
            first_name="Bob",
            username="bob",
            last_name="Smith",
            language_code="ru",
            photo_url=Url("https://example.com/a.png"),
            is_active=False,
            last_seen_at=seen,
            is_admin=True,
        )

        assert user.photo_url is not None
        assert user.photo_url.value == "https://example.com/a.png"
        assert user.username == "bob"
        assert user.last_seen_at == seen
        assert user.is_admin is True

    def test_base_entity_fields(self):
        user = User(telegram_id=TelegramId("1"), first_name="A")

        assert user.id is not None
        assert user.created_at.tzinfo is not None
        assert user.updated_at.tzinfo is not None
