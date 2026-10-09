"""Фабрика async SQLAlchemy: движок и сессии для PostgreSQL."""

from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import settings


@lru_cache
def get_engine() -> AsyncEngine:
    """Возвращает кэшированный async-движок с pool_pre_ping."""
    return create_async_engine(settings.database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Возвращает фабрику сессий с expire_on_commit=False."""
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )
