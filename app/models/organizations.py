from enum import Enum
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlmodel import Field, Relationship

from app.extras.models import BaseDBModel, MutableSABaseModel

from .managers.organizations import OrganizationModelManager

if TYPE_CHECKING:
    from .users import User


class OrganizationMemberPermission(str, Enum): ...


class OrganizationMember(MutableSABaseModel):
    id: UUID
    role: str
    permissions: list[str] = Field(
        description="A list of administrative features an organization member can perform in the organization"
    )


OrganizationMembersSAType = OrganizationMember.to_sa_type(many=True)


class Organization(BaseDBModel, table=True):
    __tablename__ = "organizations"

    name: str = Field(max_length=128, unique=True)
    is_verified: bool = Field(
        False,
        description="used to flag organizations that has been verified by eventtrakka",
    )
    logo_url: str | None = Field(None)
    about: str | None
    owner_id: UUID = Field(foreign_key="users.id")
    owner: "User" = Relationship()
    members: list[OrganizationMember] = Field(
        default_factory=list,
        sa_type=OrganizationMembersSAType,
    )

    objects: ClassVar[OrganizationModelManager["Organization"]] = (
        OrganizationModelManager()
    )
