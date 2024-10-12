from sqlmodel import SQLModel


class ResponseData[T](SQLModel):
    detail: str | None = None
    data: list[T] | T | None = None


class PaginatedDataResponseData[T](SQLModel):
    count: int
    results: list[T]
