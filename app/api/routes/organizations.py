from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUser
from app.models import Organization
from app.models.schemas.api import ResponseData
from app.models.schemas.organizations import CreateOrganization

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
async def get_organizations(current_user: CurrentUser):
    """Retrieve organizations"""
    organizations = await Organization.objects.get_organizations(current_user)
    return ResponseData[list[Organization]](
        detail="Organizations retrieved successfully", data=organizations
    )


@router.post("/{id}/transfer-ownership")
async def transfer_organization_ownership(id: UUID, current_user: CurrentUser):
    """Transfer the ownership of an organization from one user to another"""
    ...


@router.post("/{id}/update-members")
async def update_organization_members(id: UUID, current_user: CurrentUser):
    """Update the members of an organization by added or removing users"""
    ...
