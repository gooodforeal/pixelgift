from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import uuid

import jwt

from src.settings import Settings


@dataclass(frozen=True, kw_only=True)
class AccessTokenPayload:
    user_id: uuid.UUID
    exp: datetime


class JwtService:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret
        self._algorithm = settings.jwt_algorithm
        self._ttl = timedelta(minutes=settings.jwt_access_token_ttl_minutes)

    def create_access_token(self, user_id: uuid.UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "iat": int(now.timestamp()),
            "exp": int((now + self._ttl).timestamp()),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> AccessTokenPayload:
        raw = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        return AccessTokenPayload(
            user_id=uuid.UUID(raw["sub"]),
            exp=datetime.fromtimestamp(raw["exp"], tz=timezone.utc),
        )
