from pydantic import BaseModel


class CompleteTelegramLoginRequest(BaseModel):
    code: str
    telegram_id: int
    first_name: str
    username: str | None = None
    last_name: str | None = None
    language_code: str | None = None
    photo_base64: str | None = None
    photo_content_type: str | None = None


class CompleteTelegramLoginResponse(BaseModel):
    ok: bool
    reply_text: str
