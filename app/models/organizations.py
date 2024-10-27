from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from app.extras.models import BaseDBModel, MutableSABaseModel

from .managers.organizations import OrganizationModelManager

if TYPE_CHECKING:
    from .users import User


class OrganizationMemberPermission(str, Enum):
    MANAGE_EVENTS = "EVENT:WRITE"
    INVITE_MEMBERS = "MEMBERS:INVITE"
    APPROVE_REQUESTS = "MEMBERS:APPROVE_REQUEST"


class OrganizationMember(MutableSABaseModel):
    id: UUID
    role: str
    permissions: list[OrganizationMemberPermission] = Field(
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

    def is_member(
        self, user_id: UUID | None = None, user: Optional["User"] = None
    ) -> bool:
        if not any([user_id, user]):
            raise ValueError("either user_id or user must be provided")
        member_id = user_id or user.id
        member_ids = [member.id for member in self.members]
        return member_id in member_ids

    def member_has_permission(
        self,
        permission: OrganizationMemberPermission,
        user_id: UUID | None = None,
        user: Optional["User"] = None,
    ):
        if not self.is_member(user_id=user_id, user=user):
            return False
        member_id = user_id or user.id
        for member in self.members:
            if member.id == member_id:
                return permission in member.permissions
        return False


class OrganizationInviteStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


class OrganizationInvite(BaseDBModel):
    """This is used to represent an organization inviting a user to be a part of its members.

    When the owner or an organization member tries to invite a user, this model is created with
    a status of pending, an invitation email is sent to the user, if the user does not have an
    eventtrakka account, they can choose to create one. an authenticated user can then choose to
    accept the invite or decline the invite
    """

    __tablename__ = "organization_invites"

    organization_id: UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")
    status: OrganizationInviteStatus
    email: EmailStr
    permissions: list[OrganizationMemberPermission] = Field(
        description="A list of administrative features an organization member can perform in the organization"
    )


class OrganizationJoinRequest(BaseDBModel):
    """This is used to represent an authenticated user requesting to join an organization.

    An authenticated user may find an organization they belong to but have not been added as a member
    and send a request to the organization, existing members of the organizations with access to approve
    requests may choose to approve or decline the request.
    """

    __tablename__ = "organization_join_requests"

    organization_id: UUID = Field(foreign_key="organizations.id", ondelete="CASCADE")
    status: OrganizationInviteStatus
    user_id: UUID = Field(foreign_key="users.id")
