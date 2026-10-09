"""Хеширование refresh-токенов и IP для хранения в сессиях."""

from hashlib import sha256
import secrets


def generate_refresh_token() -> str:
    """Создаёт криптостойкий refresh-токен для выдачи клиенту."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw: str) -> str:
    """SHA-256 от сырого refresh-токена для поиска в БД."""
    return sha256(raw.encode("utf-8")).hexdigest()


def hash_ip(ip: str | None) -> str | None:
    """SHA-256 от IP клиента; ``None`` если адрес не передан."""
    if not ip:
        return None
    return sha256(ip.encode("utf-8")).hexdigest()
