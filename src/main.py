from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.presentation.routers import admin_designs, auth, boxes, designs, media, public
from src.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    from src.infrastructure.worker.app import broker

    await broker.startup()
    yield
    await broker.shutdown()


app = FastAPI(title="Pixelgift API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(designs.router)
app.include_router(admin_designs.router)
app.include_router(boxes.router)
app.include_router(media.router)
app.include_router(public.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
