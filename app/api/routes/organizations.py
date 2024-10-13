from uuid import UUID

from fastapi import APIRouter

from app.api.deps import CurrentUser

router = APIRouter(prefix="/organizations")


@router.post("/")
async def create_organization(current_user: CurrentUser):
    """Create an organization.

    Organizations are the different tech communities
    """
    ...


@router.get("/")
async def get_organizations(current_user: CurrentUser):
    """Retrieve organizations"""
    ...


@router.post("/{id}/transfer-ownership")
async def transfer_organization_ownership(id: UUID, current_user: CurrentUser):
    """Transfer the ownership of an organization from one user to another"""
    ...


@router.post("/{id}/update-members")
async def update_organization_members(id: UUID, current_user: CurrentUser):
    """Update the members of an organization by added or removing users"""
    ...
