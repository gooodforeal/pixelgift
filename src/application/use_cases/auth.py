from datetime import datetime, timedelta, timezone
import secrets

from src.application.dto.auth import (
    CompleteLoginResult,
    CompleteTelegramLoginCommand,
    PollTelegramLoginCommand,
    StartTelegramLoginCommand,
    TelegramLoginStartResult,
    TelegramLoginStatusResult,
)
from src.application.services.jwt import JwtService
from src.application.uow.base import BaseUnitOfWork
from src.domain.entities.telegram_login_challenges import (
    LoginChallengeStatus,
    TelegramLoginChallenge,
)
from src.domain.entities.users import User
from src.domain.exceptions.auth import (
    LoginChallengeInvalidError,
    LoginChallengeNotFoundError,
    UserInactiveError,
)
from src.domain.values.telegram_id import TelegramId
from src.settings import Settings


def generate_login_code() -> str:
    return secrets.token_urlsafe(32)


class StartTelegramLoginUseCase:
    def __init__(self, uow: BaseUnitOfWork, settings: Settings) -> None:
        self._uow = uow
        self._settings = settings

    async def execute(
        self, command: StartTelegramLoginCommand
    ) -> TelegramLoginStartResult:
        code = generate_login_code()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.login_challenge_ttl_minutes
        )
        challenge = TelegramLoginChallenge(
            code=code,
            status=LoginChallengeStatus.PENDING,
            expires_at=expires_at,
            client_ip_hash=command.client_ip_hash,
        )

        async with self._uow as uow:
            await uow.telegram_login_challenges.add(challenge)
            await uow.commit()

        bot_username = self._settings.telegram_bot_username.lstrip("@")
        bot_url = f"https://t.me/{bot_username}?start=login_{code}"
        return TelegramLoginStartResult(
            code=code,
            bot_url=bot_url,
            expires_at=expires_at.isoformat(),
        )


class PollTelegramLoginStatusUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        jwt_service: JwtService,
    ) -> None:
        self._uow = uow
        self._jwt_service = jwt_service

    async def execute(
        self, command: PollTelegramLoginCommand
    ) -> TelegramLoginStatusResult:
        async with self._uow as uow:
            challenge = await uow.telegram_login_challenges.get_by_code(command.code)
            if challenge is None:
                raise LoginChallengeNotFoundError(command.code)

            now = datetime.now(timezone.utc)
            if (
                challenge.status == LoginChallengeStatus.PENDING
                and challenge.expires_at <= now
            ):
                challenge.status = LoginChallengeStatus.EXPIRED
                await uow.telegram_login_challenges.update(challenge)
                await uow.commit()
                return TelegramLoginStatusResult(status=LoginChallengeStatus.EXPIRED)

            if challenge.status == LoginChallengeStatus.EXPIRED:
                return TelegramLoginStatusResult(status=LoginChallengeStatus.EXPIRED)

            if challenge.status == LoginChallengeStatus.PENDING:
                return TelegramLoginStatusResult(status=LoginChallengeStatus.PENDING)

            if challenge.user_id is None:
                raise LoginChallengeInvalidError(command.code)

            user = await uow.users.get_by_id(challenge.user_id)
            if user is None or not user.is_active:
                raise UserInactiveError(challenge.user_id)

            access_token = self._jwt_service.create_access_token(user.id)
            return TelegramLoginStatusResult(
                status=LoginChallengeStatus.COMPLETED,
                access_token=access_token,
                token_type="bearer",
                user_id=user.id,
            )


class CompleteTelegramLoginUseCase:
    """Completes a pending login challenge after Telegram /start login_<code>."""

    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: CompleteTelegramLoginCommand) -> CompleteLoginResult:
        async with self._uow as uow:
            challenge = await uow.telegram_login_challenges.get_by_code(command.code)
            if challenge is None:
                return CompleteLoginResult(
                    ok=False,
                    reply_text="Код входа не найден. Начните вход заново на сайте.",
                )

            now = datetime.now(timezone.utc)
            if challenge.status == LoginChallengeStatus.COMPLETED:
                return CompleteLoginResult(
                    ok=False,
                    reply_text="Этот код уже использован. Начните вход заново на сайте.",
                )

            if (
                challenge.status == LoginChallengeStatus.EXPIRED
                or challenge.expires_at <= now
            ):
                if challenge.status != LoginChallengeStatus.EXPIRED:
                    challenge.status = LoginChallengeStatus.EXPIRED
                    await uow.telegram_login_challenges.update(challenge)
                    await uow.commit()
                return CompleteLoginResult(
                    ok=False,
                    reply_text="Код входа истёк. Начните вход заново на сайте.",
                )

            if challenge.status != LoginChallengeStatus.PENDING:
                return CompleteLoginResult(
                    ok=False,
                    reply_text="Код входа недействителен. Начните вход заново на сайте.",
                )

            telegram_id = TelegramId(str(command.telegram_id))
            user = await uow.users.get_by_telegram_id(command.telegram_id)
            if user is None:
                user = User(
                    telegram_id=telegram_id,
                    first_name=command.first_name,
                    username=command.username,
                    last_name=command.last_name,
                    language_code=command.language_code,
                    last_seen_at=now,
                )
                await uow.users.add(user)
            else:
                user.first_name = command.first_name
                user.username = command.username
                user.last_name = command.last_name
                user.language_code = command.language_code
                user.last_seen_at = now
                await uow.users.update(user)

            challenge.status = LoginChallengeStatus.COMPLETED
            challenge.telegram_id = telegram_id
            challenge.user_id = user.id
            challenge.completed_at = now
            await uow.telegram_login_challenges.update(challenge)
            await uow.commit()

        return CompleteLoginResult(
            ok=True,
            reply_text="Вход выполнен. Вернитесь на сайт.",
        )
