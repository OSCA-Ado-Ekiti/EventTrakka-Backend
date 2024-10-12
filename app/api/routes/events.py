from fastapi import APIRouter
from uuid import UUID

router = APIRouter(prefix="/events")


@router.post("/")
async def create_event():
    """Create a tech event"""
    ...


@router.get("/")
async def get_events():
    """Retrieve created tech events"""
    ...


@router.patch("/{id}")
async def partial_update_event(id: UUID):
    """Update a tech events"""
    ...
