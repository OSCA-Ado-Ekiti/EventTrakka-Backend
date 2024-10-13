from uuid import UUID

from fastapi import APIRouter

from app.api.deps import CurrentUser

router = APIRouter(prefix="/events")


@router.post("/")
async def create_event(current_user: CurrentUser):
    """Create a tech event"""
    ...


@router.get("/")
async def get_events(current_user: CurrentUser):
    """Retrieve created tech events"""
    ...


@router.patch("/{id}")
async def partial_update_event(id: UUID, current_user: CurrentUser):
    """Update a tech events"""
    ...
