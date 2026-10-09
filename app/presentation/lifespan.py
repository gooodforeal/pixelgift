"""Жизненный цикл FastAPI: старт и остановка фонового брокера задач."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Запускает Taskiq-брокер при старте приложения и останавливает при shutdown."""
    from app.infrastructure.worker.app import broker

    await broker.startup()
    yield
    await broker.shutdown()
