from datetime import datetime, timedelta, timezone

import pytest

from src.application.dto.auth import (
    CompleteTelegramLoginCommand,
    LogoutCommand,
    PollTelegramLoginCommand,
    RefreshAccessTokenCommand,
    StartTelegramLoginCommand,
)
from src.application.services.jwt import JwtService
from src.application.services.refresh_tokens import hash_refresh_token
from src.application.use_cases.auth import (
    CompleteTelegramLoginUseCase,
    LogoutUseCase,
    PollTelegramLoginStatusUseCase,
    RefreshAccessTokenUseCase,
    StartTelegramLoginUseCase,
)
from src.domain.entities.telegram_login_challenges import LoginChallengeStatus
from src.domain.exceptions.auth import (
    InvalidRefreshTokenError,
    LoginChallengeNotFoundError,
)
from src.settings import Settings
from tests.application.fakes import InMemoryUnitOfWork


@pytest.fixture
def auth_settings() -> Settings:
    return Settings(
        telegram_bot_username="pixelgift_bot",
        jwt_secret="test-secret-key-at-least-32-bytes!!",
        jwt_access_token_ttl_minutes=15,
        jwt_refresh_token_ttl_days=30,
        login_challenge_ttl_minutes=10,
    )


async def _complete_login(uow: InMemoryUnitOfWork, settings: Settings):
    start = StartTelegramLoginUseCase(uow, settings)
    started = await start.execute(StartTelegramLoginCommand())
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
    return started.code


class TestTelegramAuthUseCases:
    async def test_start_and_complete_login(self, auth_settings: Settings):
        uow = InMemoryUnitOfWork()
        code = await _complete_login(uow, auth_settings)

        poll = PollTelegramLoginStatusUseCase(
            uow, JwtService(auth_settings), auth_settings
        )
        status = await poll.execute(
            PollTelegramLoginCommand(
                code=code,
                user_agent="pytest",
                client_ip="127.0.0.1",
            )
        )
        assert status.status == LoginChallengeStatus.COMPLETED
        assert status.access_token
        assert status.refresh_token
        assert status.user_id is not None

        sessions = await uow.user_sessions.list_by_user_id(status.user_id)
        assert len(sessions) == 1
        assert sessions[0].refresh_token_hash == hash_refresh_token(
            status.refresh_token
        )
        assert sessions[0].revoked_at is None
        assert sessions[0].user_agent == "pytest"

        payload = JwtService(auth_settings).decode_access_token(status.access_token)
        assert payload.user_id == status.user_id

        challenge = await uow.telegram_login_challenges.get_by_code(code)
        assert challenge is not None
        assert challenge.status == LoginChallengeStatus.CONSUMED

        second = await poll.execute(
            PollTelegramLoginCommand(code=code, user_agent="pytest")
        )
        assert second.status == LoginChallengeStatus.CONSUMED
        assert second.access_token is None
        assert second.refresh_token is None
        assert len(await uow.user_sessions.list_by_user_id(status.user_id)) == 1

    async def test_poll_unknown_code(self, auth_settings: Settings):
        poll = PollTelegramLoginStatusUseCase(
            InMemoryUnitOfWork(), JwtService(auth_settings), auth_settings
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

        poll = PollTelegramLoginStatusUseCase(
            uow, JwtService(auth_settings), auth_settings
        )
        status = await poll.execute(PollTelegramLoginCommand(code=started.code))
        assert status.status == LoginChallengeStatus.EXPIRED

    async def test_refresh_rotates_session(self, auth_settings: Settings):
        uow = InMemoryUnitOfWork()
        code = await _complete_login(uow, auth_settings)
        poll = PollTelegramLoginStatusUseCase(
            uow, JwtService(auth_settings), auth_settings
        )
        status = await poll.execute(PollTelegramLoginCommand(code=code))
        assert status.refresh_token

        refresh = RefreshAccessTokenUseCase(
            uow, JwtService(auth_settings), auth_settings
        )
        pair = await refresh.execute(
            RefreshAccessTokenCommand(refresh_token=status.refresh_token)
        )
        assert pair.access_token
        assert pair.refresh_token != status.refresh_token

        old = await uow.user_sessions.get_by_refresh_token_hash(
            hash_refresh_token(status.refresh_token)
        )
        assert old is not None
        assert old.revoked_at is not None

        new = await uow.user_sessions.get_by_refresh_token_hash(
            hash_refresh_token(pair.refresh_token)
        )
        assert new is not None
        assert new.revoked_at is None

        with pytest.raises(InvalidRefreshTokenError):
            await refresh.execute(
                RefreshAccessTokenCommand(refresh_token=status.refresh_token)
            )

    async def test_logout_revokes_session(self, auth_settings: Settings):
        uow = InMemoryUnitOfWork()
        code = await _complete_login(uow, auth_settings)
        poll = PollTelegramLoginStatusUseCase(
            uow, JwtService(auth_settings), auth_settings
        )
        status = await poll.execute(PollTelegramLoginCommand(code=code))
        assert status.refresh_token

        logout = LogoutUseCase(uow)
        await logout.execute(LogoutCommand(refresh_token=status.refresh_token))

        session = await uow.user_sessions.get_by_refresh_token_hash(
            hash_refresh_token(status.refresh_token)
        )
        assert session is not None
        assert session.revoked_at is not None

        refresh = RefreshAccessTokenUseCase(
            uow, JwtService(auth_settings), auth_settings
        )
        with pytest.raises(InvalidRefreshTokenError):
            await refresh.execute(
                RefreshAccessTokenCommand(refresh_token=status.refresh_token)
            )
