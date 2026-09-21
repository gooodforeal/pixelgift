from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse

from app.presentation.admin import setup_admin
from app.presentation.routers import (
    admin_designs,
    admin_support,
    auth,
    boxes,
    designs,
    media,
    public,
    support,
)
from app.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    from app.infrastructure.worker.app import broker

    await broker.startup()
    yield
    await broker.shutdown()


app = FastAPI(
    title="Pixelgift API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

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
app.include_router(admin_support.router)
app.include_router(boxes.router)
app.include_router(media.router)
app.include_router(public.router)
app.include_router(support.router)
setup_admin(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/docs", include_in_schema=False)
async def swagger_ui() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="openapi.json",
        title=f"{app.title} - Docs",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_ui() -> HTMLResponse:
    return get_redoc_html(
        openapi_url="openapi.json",
        title=f"{app.title} - ReDoc",
    )
