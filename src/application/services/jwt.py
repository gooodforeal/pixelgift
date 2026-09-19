from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import uuid

import jwt

from src.settings import Settings


@dataclass(frozen=True, kw_only=True)
class AccessTokenPayload:
    user_id: uuid.UUID
    exp: datetime


@dataclass(frozen=True, kw_only=True)
class BoxUnlockTokenPayload:
    box_id: uuid.UUID
    public_slug: str
    exp: datetime


class JwtService:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret
        self._algorithm = settings.jwt_algorithm
        self._ttl = timedelta(minutes=settings.jwt_access_token_ttl_minutes)
        self._unlock_ttl = timedelta(days=30)

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

    def create_box_unlock_token(self, *, box_id: uuid.UUID, public_slug: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "typ": "box_unlock",
            "box_id": str(box_id),
            "slug": public_slug,
            "iat": int(now.timestamp()),
            "exp": int((now + self._unlock_ttl).timestamp()),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_box_unlock_token(self, token: str) -> BoxUnlockTokenPayload:
        raw = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        if raw.get("typ") != "box_unlock":
            raise jwt.InvalidTokenError("Not a box unlock token")
        return BoxUnlockTokenPayload(
            box_id=uuid.UUID(raw["box_id"]),
            public_slug=str(raw["slug"]),
            exp=datetime.fromtimestamp(raw["exp"], tz=timezone.utc),
        )
