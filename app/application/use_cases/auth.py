"""Вход через Telegram-бота, сессии JWT и настройки пользователя."""

from datetime import datetime, timedelta, timezone
import secrets

from app.application.dto.auth import (
    CompleteLoginResult,
    CompleteTelegramLoginCommand,
    LogoutCommand,
    PollTelegramLoginCommand,
    RefreshAccessTokenCommand,
    StartTelegramLoginCommand,
    TelegramLoginStartResult,
    TelegramLoginStatusResult,
    TokenPairResult,
    UpdateCurrentUserSettingsCommand,
)
from app.application.ports.storage.base import BaseObjectStorage
from app.application.services.jwt import JwtService
from app.application.services.refresh_tokens import (
    generate_refresh_token,
    hash_ip,
    hash_refresh_token,
)
from app.application.uow.base import BaseUnitOfWork
from app.domain.entities.telegram_login_challenges import (
    LoginChallengeStatus,
    TelegramLoginChallenge,
)
from app.domain.entities.user_sessions import UserSession
from app.domain.entities.users import User
from app.domain.exceptions.auth import (
    InvalidRefreshTokenError,
    LoginChallengeInvalidError,
    LoginChallengeNotFoundError,
    UserInactiveError,
)
from app.domain.exceptions.users import UserNotFoundError
from app.domain.values.telegram_id import TelegramId
from app.domain.values.url import Url
from app.settings import Settings


def generate_login_code() -> str:
    """Одноразовый код для deep-link ``login_<code>`` в боте."""
    return secrets.token_urlsafe(32)


def avatar_storage_key(user_id) -> str:
    """Ключ object storage для аватара пользователя."""
    return f"avatars/{user_id}"


def _truncate_user_agent(user_agent: str | None) -> str | None:
    if not user_agent:
        return None
    return user_agent[:512]


class StartTelegramLoginUseCase:
    """Создаёт челлендж входа и ссылку на Telegram-бота."""

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
    """Клиент опрашивает код; при успехе в боте выдаёт access/refresh и потребляет челлендж."""

    def __init__(
        self,
        uow: BaseUnitOfWork,
        jwt_service: JwtService,
        settings: Settings,
    ) -> None:
        self._uow = uow
        self._jwt_service = jwt_service
        self._settings = settings

    async def execute(
        self, command: PollTelegramLoginCommand
    ) -> TelegramLoginStatusResult:
        async with self._uow as uow:
            challenge = await uow.telegram_login_challenges.get_by_code(
                command.code, for_update=True
            )
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

            if challenge.status == LoginChallengeStatus.CONSUMED:
                return TelegramLoginStatusResult(
                    status=LoginChallengeStatus.CONSUMED,
                    user_id=challenge.user_id,
                )

            if challenge.status != LoginChallengeStatus.COMPLETED:
                raise LoginChallengeInvalidError(command.code)

            if challenge.user_id is None:
                raise LoginChallengeInvalidError(command.code)

            user = await uow.users.get_by_id(challenge.user_id)
            if user is None or not user.is_active:
                raise UserInactiveError(challenge.user_id)

            challenge.status = LoginChallengeStatus.CONSUMED
            await uow.telegram_login_challenges.update(challenge)

            raw_refresh = generate_refresh_token()
            session = UserSession(
                user_id=user.id,
                refresh_token_hash=hash_refresh_token(raw_refresh),
                expires_at=now
                + timedelta(days=self._settings.jwt_refresh_token_ttl_days),
                user_agent=_truncate_user_agent(command.user_agent),
                ip_hash=hash_ip(command.client_ip),
            )
            await uow.user_sessions.add(session)
            await uow.commit()

            access_token = self._jwt_service.create_access_token(user.id)
            return TelegramLoginStatusResult(
                status=LoginChallengeStatus.COMPLETED,
                access_token=access_token,
                refresh_token=raw_refresh,
                token_type="bearer",
                user_id=user.id,
            )


class RefreshAccessTokenUseCase:
    """Ротация refresh-токена: отзыв старой сессии и выдача новой пары."""

    def __init__(
        self,
        uow: BaseUnitOfWork,
        jwt_service: JwtService,
        settings: Settings,
    ) -> None:
        self._uow = uow
        self._jwt_service = jwt_service
        self._settings = settings

    async def execute(self, command: RefreshAccessTokenCommand) -> TokenPairResult:
        token_hash = hash_refresh_token(command.refresh_token)
        now = datetime.now(timezone.utc)

        async with self._uow as uow:
            session = await uow.user_sessions.get_by_refresh_token_hash(token_hash)
            if (
                session is None
                or session.revoked_at is not None
                or session.expires_at <= now
            ):
                raise InvalidRefreshTokenError()

            user = await uow.users.get_by_id(session.user_id)
            if user is None or not user.is_active:
                session.revoked_at = now
                await uow.user_sessions.update(session)
                await uow.commit()
                raise UserInactiveError(session.user_id)

            session.revoked_at = now
            await uow.user_sessions.update(session)

            raw_refresh = generate_refresh_token()
            new_session = UserSession(
                user_id=user.id,
                refresh_token_hash=hash_refresh_token(raw_refresh),
                expires_at=now
                + timedelta(days=self._settings.jwt_refresh_token_ttl_days),
                user_agent=_truncate_user_agent(command.user_agent)
                or session.user_agent,
                ip_hash=hash_ip(command.client_ip) or session.ip_hash,
            )
            await uow.user_sessions.add(new_session)
            await uow.commit()

        return TokenPairResult(
            access_token=self._jwt_service.create_access_token(user.id),
            refresh_token=raw_refresh,
            user_id=user.id,
        )


class LogoutUseCase:
    """Отзывает сессию по refresh-токену (идемпотентно)."""

    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: LogoutCommand) -> None:
        if not command.refresh_token:
            return

        token_hash = hash_refresh_token(command.refresh_token)
        now = datetime.now(timezone.utc)

        async with self._uow as uow:
            session = await uow.user_sessions.get_by_refresh_token_hash(token_hash)
            if session is None or session.revoked_at is not None:
                return
            session.revoked_at = now
            await uow.user_sessions.update(session)
            await uow.commit()


class CompleteTelegramLoginUseCase:
    """Вызывается ботом: подтверждает код, создаёт/обновляет пользователя и аватар."""

    def __init__(
        self,
        uow: BaseUnitOfWork,
        storage: BaseObjectStorage | None = None,
        *,
        api_base_url: str = "http://localhost:8080/api",
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._api_base_url = api_base_url.rstrip("/")

    async def execute(self, command: CompleteTelegramLoginCommand) -> CompleteLoginResult:
        async with self._uow as uow:
            challenge = await uow.telegram_login_challenges.get_by_code(command.code)
            if challenge is None:
                return CompleteLoginResult(
                    ok=False,
                    reply_text="Код входа не найден. Начните вход заново на сайте.",
                )

            now = datetime.now(timezone.utc)
            if challenge.status in (
                LoginChallengeStatus.COMPLETED,
                LoginChallengeStatus.CONSUMED,
            ):
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

        if (
            self._storage is not None
            and command.photo_bytes
            and len(command.photo_bytes) > 0
        ):
            content_type = command.photo_content_type or "image/jpeg"
            try:
                await self._storage.upload(
                    avatar_storage_key(user.id),
                    command.photo_bytes,
                    content_type=content_type,
                )
                async with self._uow as uow:
                    stored = await uow.users.get_by_id(user.id)
                    if stored is not None:
                        stored.photo_url = Url(
                            f"{self._api_base_url}/users/{stored.id}/avatar"
                        )
                        await uow.users.update(stored)
                        await uow.commit()
            except Exception:
                pass

        return CompleteLoginResult(
            ok=True,
            reply_text="Вход выполнен. Вернитесь на сайт.",
        )


class UpdateCurrentUserSettingsUseCase:
    """Обновляет настройки профиля (например, Telegram-уведомления)."""

    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: UpdateCurrentUserSettingsCommand) -> User:
        async with self._uow as uow:
            user = await uow.users.get_by_id(command.user_id)
            if user is None:
                raise UserNotFoundError(command.user_id)
            if not user.is_active:
                raise UserInactiveError(command.user_id)

            if command.notifications_enabled is not None:
                user.notifications_enabled = command.notifications_enabled

            await uow.users.update(user)
            await uow.commit()
            return user

