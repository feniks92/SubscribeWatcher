from typing import Literal, Optional

from pydantic import BaseModel, Field


class Docs(BaseModel):
    swagger_ui: str = Field('/api/v1/docs', alias="swaggerUI")
    redoc_ui: str = Field('/api/v1/redoc', alias="redocUI")
    openapi: str = Field('/api/v1/openapi.json', alias="openapi")


class StatusResponse(BaseModel):
    status: str = Field('OK')
    version: str = Field(..., example='dev.3c257a1')
    release: Optional[str] = Field(None, example="beta_10")
    docs: Optional[Docs]


class Problem(BaseModel):
    """Model of the RFC7807 Problem response schema."""

    type: str
    title: str
    status: Optional[int]
    detail: Optional[str]
    instance: Optional[str]
