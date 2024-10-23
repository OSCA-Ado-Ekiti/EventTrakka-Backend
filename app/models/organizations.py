from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import JSON, Field, Relationship, SQLModel

from app.extras.models import BaseDBModel

if TYPE_CHECKING:
    from .users import User


class OrganizationMemberPermission(str, Enum): ...


class OrganizationMember(SQLModel):
    id: UUID
    role: str
    permissions: list[str] = Field(
        description="A list of administrative features an organization member can perform in the organization"
    )


class Organization(BaseDBModel, table=True):
    __tablename__ = "organizations"

    name: str = Field(max_length=128)
    is_verified: bool
    logo_url: str | None
    about: str | None
    owner_id: UUID = Field(foreign_key="users.id")
    owner: "User" = Relationship()
    members: list[OrganizationMember] = Field(default_factory=list, sa_type=JSON())
