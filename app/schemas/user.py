from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE_PATTERN = r"^\+[1-9]\d{1,14}$"


class AddressSchema(BaseModel):
    line1: str
    line2: str | None = None
    line3: str | None = None
    town: str
    county: str
    postcode: str


class CreateUserRequest(BaseModel):
    name: str
    address: AddressSchema
    phoneNumber: str = Field(pattern=PHONE_PATTERN)
    email: str = Field(pattern=EMAIL_PATTERN)
    password: str = Field(min_length=8)


class UpdateUserRequest(BaseModel):
    name: str | None = None
    address: AddressSchema | None = None
    phoneNumber: str | None = Field(default=None, pattern=PHONE_PATTERN)
    email: str | None = Field(default=None, pattern=EMAIL_PATTERN)
    password: str | None = Field(default=None, min_length=8)


class UserResponse(BaseModel):
    id: str
    name: str
    address: AddressSchema
    phoneNumber: str
    email: str
    createdTimestamp: datetime
    updatedTimestamp: datetime
