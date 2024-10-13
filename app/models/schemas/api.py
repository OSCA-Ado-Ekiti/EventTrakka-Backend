from uuid import UUID

from sqlmodel import SQLModel


class ResponseData[T](SQLModel):
    detail: str | None = None
    data: list[T] | T | None = None


class PaginatedDataResponseData[T](SQLModel):
    count: int
    results: list[T]


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenSubject(SQLModel):
    type: str = "access_token"
    user: UUID
    scope: list[str] = []


class RefreshTokenSubject(SQLModel):
    type: str = "refresh_token"
    user: UUID
