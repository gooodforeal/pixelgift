from dataclasses import dataclass
import uuid


@dataclass(frozen=True, kw_only=True)
class StartTelegramLoginCommand:
    client_ip_hash: str | None = None


@dataclass(frozen=True, kw_only=True)
class PollTelegramLoginCommand:
    code: str


@dataclass(frozen=True, kw_only=True)
class CompleteTelegramLoginCommand:
    code: str
    telegram_id: int
    first_name: str
    username: str | None = None
    last_name: str | None = None
    language_code: str | None = None


@dataclass(frozen=True, kw_only=True)
class TelegramLoginStartResult:
    code: str
    bot_url: str
    expires_at: str


@dataclass(frozen=True, kw_only=True)
class TelegramLoginStatusResult:
    status: str
    access_token: str | None = None
    token_type: str | None = None
    user_id: uuid.UUID | None = None


@dataclass(frozen=True, kw_only=True)
class CompleteLoginResult:
    ok: bool
    reply_text: str
