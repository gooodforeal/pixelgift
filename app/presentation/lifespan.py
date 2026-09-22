from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    from app.infrastructure.worker.app import broker

    await broker.startup()
    yield
    await broker.shutdown()
