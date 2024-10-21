from typing import Literal
from uuid import UUID

from sqlmodel import SQLModel

from app.core.security import APIScope


class ResponseData[T](SQLModel):
    detail: str | None = None
    data: list[T] | T | None = None


class PaginatedDataResponseData[T](SQLModel):
    count: int
    results: list[T]


class Token(SQLModel):
    token_type: str = "bearer"


class AuthToken(Token):
    access_token: str
    refresh_token: str


class VerificationToken(Token):
    verification_token: str | None


class TokenSubject(SQLModel):
    type: Literal["access_token", "refresh_token", "verification_token"]
    user_id: UUID
    scopes: list[APIScope] = []


class PasswordReset(SQLModel):
    user_id: UUID
    otp: str
    new_password: str
