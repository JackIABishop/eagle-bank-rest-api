from __future__ import annotations

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


class ValidationErrorDetail(BaseModel):
    field: str
    message: str
    type: str


class BadRequestErrorResponse(BaseModel):
    message: str
    details: list[ValidationErrorDetail]
