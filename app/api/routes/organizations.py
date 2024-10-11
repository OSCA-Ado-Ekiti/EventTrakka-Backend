from fastapi import APIRouter

router = APIRouter(prefix="/organizations")


@router.post("/")
async def create_organization():
    """Create an organization.

    Organizations are the different tech communities
    """
    ...


@router.get("/")
async def get_organizations():
    """Retrieve organizations"""
    ...


@router.post("/{id}/transfer-ownership")
async def transfer_organization_ownership():
    """Transfer the ownership of an organization from one user to another"""
    ...


@router.post("/{id}/update-members")
async def update_organization_members():
    """Update the members of an organization by added or removing users"""
    ...
