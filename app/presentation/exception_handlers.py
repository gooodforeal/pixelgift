import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions.base import BaseException as DomainException
from app.presentation.schemas.errors import ErrorResponseSchema

logger = logging.getLogger(__name__)


def _error_body(message: str) -> dict:
    return ErrorResponseSchema(message=message, result=None).model_dump()


async def domain_exception_handler(
    request: Request,
    exc: DomainException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.message),
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, str):
        message = detail
    else:
        message = str(detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(message),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    message = "; ".join(
        f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
        for err in exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content=_error_body(message or "Validation error"),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=_error_body("Internal server error"),
    )
