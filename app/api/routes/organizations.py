from fastapi import APIRouter

router = APIRouter(prefix="/organizations")

@router.post('/')
async def create_organization():
    ...

@router.get('/')
async def get_organizations():
    ...

@router.post('/{id}/transfer-ownership')
async def transfer_organization_ownership():
    ...

@router.post('/{id}/update-members')
async def update_organization_members():
    ...