from __future__ import annotations

from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class LoginRequest(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN)
    password: str = Field(min_length=8)


class AuthTokenResponse(BaseModel):
    accessToken: str
    tokenType: str
    expiresIn: int
