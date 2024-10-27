from uuid import UUID

from sqlmodel import SQLModel


class CreateOrganization(SQLModel):
    name: str
    about: str | None = None


class OrganizationPublic(SQLModel):
    id: UUID
    name: str
    is_verified: bool
    logo_url: str | None
    about: str | None
