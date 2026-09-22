from pydantic import BaseModel

from app.presentation.schemas.base import BaseResponseSchema


class HealthSchema(BaseModel):
    status: str


class HealthResponse(BaseResponseSchema[HealthSchema]):
    pass
