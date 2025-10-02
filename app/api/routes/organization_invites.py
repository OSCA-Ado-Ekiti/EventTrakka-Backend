from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page

from app.api.deps import AuthenticatedUser
from app.models import Organization, User
from app.models.organizations import (
    MembershipInvite,
    MembershipStatus,
    OrganizationMember,
)

router = APIRouter(prefix="/organization-invites")


async def approve_or_decline_invite(
    id: UUID,
    user: User,
    invite_status: Literal[MembershipStatus.ACCEPTED, MembershipStatus.DECLINED],
) -> MembershipInvite:
    try:
        invite: MembershipInvite = await MembershipInvite.objects.get(
            MembershipInvite.id == id, MembershipInvite.email == user.email
        )
    except MembershipInvite.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invite not found"
        )
    if invite.status != MembershipStatus.PENDING:
        detail = {
            MembershipStatus.EXPIRED: "invite has expired",
            MembershipStatus.ACCEPTED: "invite has been approved",
            MembershipStatus.DECLINED: "invite has been declined",
        }[invite.status]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )
    invite.status = invite_status
    return await MembershipInvite.objects.update(model=invite)


@router.get("/")
async def get_organization_invites(
    current_user: AuthenticatedUser,
) -> Page[MembershipInvite]:
    return await MembershipInvite.objects.many(
        MembershipInvite.email == current_user.email
    )


@router.post("/{id}/approve/")
async def approve_organization_invite(id: UUID, current_user: AuthenticatedUser):
    invite = await approve_or_decline_invite(
        id, current_user, MembershipStatus.ACCEPTED
    )
    organization: Organization = await Organization.objects.get(
        Organization.id == invite.organization_id
    )
    member = OrganizationMember.model_validate(
        {"id": current_user.id, "role": None, "permissions": []}
    )
    organization.members.append(member)
    await organization.objects.update(model=organization)
    # TODO: Send email to member of the organization who initiated the invite that
    # the recipient honoured the invite.
    return invite


@router.post("/{id}/decline/")
async def decline_organization_invite(id: UUID, current_user: AuthenticatedUser):
    # TODO: Send email to member of the organization who initiated the invite that
    # the recipient dishonoured the invite.
    return await approve_or_decline_invite(id, current_user, MembershipStatus.DECLINED)
