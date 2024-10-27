from uuid import UUID

from fastapi import APIRouter, status
from fastapi_pagination import Page

from app.api.deps import CurrentUser
from app.core.utils import ENDPOINT_NOT_IMPLEMENTED
from app.models import Event, Organization
from app.models.events import EventPublicationStatus
from app.models.schemas.api import ResponseData
from app.models.schemas.organizations import CreateOrganization, OrganizationPublic

router = APIRouter(prefix="/organizations")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_organization(current_user: CurrentUser, data: CreateOrganization):
    """Create an organization.

    Organizations are the different tech communities
    """
    organization = await Organization.objects.create_organization(
        name=data.name, owner=current_user, about=data.about
    )
    return ResponseData[Organization](
        detail="Organization successfully created", data=organization
    )


@router.get("/")
async def get_organizations_as_member(current_user: CurrentUser) -> Page[Organization]:
    """Retrieve organizations"""
    return await Organization.objects.get_organizations_as_member(current_user)


@router.get("/public/")
async def get_organizations_as_public() -> Page[OrganizationPublic]:
    return await Organization.objects.all()


@router.post("/{id}/transfer-ownership/")
async def transfer_organization_ownership(id: UUID, current_user: CurrentUser):
    """Transfer the ownership of an organization from one user to another"""
    raise ENDPOINT_NOT_IMPLEMENTED


@router.post("/{id}/update-members/")
async def update_organization_members(id: UUID, current_user: CurrentUser):
    """Update the members of an organization by added or removing users"""
    raise ENDPOINT_NOT_IMPLEMENTED


@router.get("{id}/events/")
async def get_events(id: UUID, current_user: CurrentUser) -> Page[Event]:
    """Retrieve created tech events"""
    return await Event.objects.filter(
        Event.organization_id == id, Event.status != EventPublicationStatus.ARCHIVE
    )
