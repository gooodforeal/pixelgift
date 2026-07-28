import uuid

from pydantic import BaseModel


class TelegramLoginStartResponse(BaseModel):
    code: str
    bot_url: str
    expires_at: str


class TelegramLoginStatusResponse(BaseModel):
    status: str
    access_token: str | None = None
    token_type: str | None = None
    user_id: uuid.UUID | None = None


class CompleteTelegramLoginRequest(BaseModel):
    code: str
    telegram_id: int
    first_name: str
    username: str | None = None
    last_name: str | None = None
    language_code: str | None = None


class CompleteTelegramLoginResponse(BaseModel):
    ok: bool
    reply_text: str
