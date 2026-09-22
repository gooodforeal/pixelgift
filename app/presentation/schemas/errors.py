from app.presentation.schemas.base import BaseResponseSchema


class ErrorResponseSchema(BaseResponseSchema[None]):
    result: None = None
