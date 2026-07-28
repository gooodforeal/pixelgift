from datetime import datetime, timedelta, timezone

import pytest

from src.application.dto.auth import (
    CompleteTelegramLoginCommand,
    PollTelegramLoginCommand,
    StartTelegramLoginCommand,
)
from src.application.services.jwt import JwtService
from src.application.use_cases.auth import (
    CompleteTelegramLoginUseCase,
    PollTelegramLoginStatusUseCase,
    StartTelegramLoginUseCase,
)
from src.domain.entities.telegram_login_challenges import LoginChallengeStatus
from src.domain.exceptions.auth import LoginChallengeNotFoundError
from src.settings import Settings
from tests.application.fakes import InMemoryUnitOfWork


@pytest.fixture
def auth_settings() -> Settings:
    return Settings(
        telegram_bot_username="pixelgift_bot",
        jwt_secret="test-secret-key-at-least-32-bytes!!",
        login_challenge_ttl_minutes=10,
    )


class TestTelegramAuthUseCases:
    async def test_start_and_complete_login(self, auth_settings: Settings):
        uow = InMemoryUnitOfWork()
        start = StartTelegramLoginUseCase(uow, auth_settings)
        started = await start.execute(StartTelegramLoginCommand())

        assert started.code
        assert started.bot_url.startswith("https://t.me/pixelgift_bot?start=login_")

        complete = CompleteTelegramLoginUseCase(uow)
        result = await complete.execute(
            CompleteTelegramLoginCommand(
                code=started.code,
                telegram_id=123456,
                first_name="Tim",
                username="tim",
            )
        )
        assert result.ok is True
        assert "сайт" in result.reply_text

        poll = PollTelegramLoginStatusUseCase(uow, JwtService(auth_settings))
        status = await poll.execute(PollTelegramLoginCommand(code=started.code))
        assert status.status == LoginChallengeStatus.COMPLETED
        assert status.access_token
        assert status.user_id is not None

        payload = JwtService(auth_settings).decode_access_token(status.access_token)
        assert payload.user_id == status.user_id

    async def test_poll_unknown_code(self, auth_settings: Settings):
        poll = PollTelegramLoginStatusUseCase(
            InMemoryUnitOfWork(), JwtService(auth_settings)
        )
        with pytest.raises(LoginChallengeNotFoundError):
            await poll.execute(PollTelegramLoginCommand(code="missing"))

    async def test_expired_challenge(self, auth_settings: Settings):
        uow = InMemoryUnitOfWork()
        start = StartTelegramLoginUseCase(uow, auth_settings)
        started = await start.execute(StartTelegramLoginCommand())
        challenge = await uow.telegram_login_challenges.get_by_code(started.code)
        assert challenge is not None
        challenge.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        await uow.telegram_login_challenges.update(challenge)

        poll = PollTelegramLoginStatusUseCase(uow, JwtService(auth_settings))
        status = await poll.execute(PollTelegramLoginCommand(code=started.code))
        assert status.status == LoginChallengeStatus.EXPIRED
