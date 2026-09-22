from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.domain.exceptions.base import BaseException as DomainException
from app.presentation.admin import setup_admin
from app.presentation.exception_handlers import (
    domain_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.presentation.lifespan import lifespan
from app.presentation.middleware import setup_middleware
from app.presentation.routers import (
    admin_designs,
    admin_support,
    auth,
    boxes,
    designs,
    docs,
    health,
    media,
    public,
    support,
)

app = FastAPI(
    title="Pixelgift API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

setup_middleware(app)

app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(health.router)
app.include_router(docs.router)
app.include_router(auth.router)
app.include_router(designs.router)
app.include_router(admin_designs.router)
app.include_router(admin_support.router)
app.include_router(boxes.router)
app.include_router(media.router)
app.include_router(public.router)
app.include_router(support.router)
setup_admin(app)
