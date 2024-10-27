from fastapi import APIRouter

from app.core.utils import ENDPOINT_NOT_IMPLEMENTED

router = APIRouter(prefix="/attendees")


@router.post("/")
async def create_attendee():
    """Create an attendees.

    Attendees are users who sign up for an event
    """
    raise ENDPOINT_NOT_IMPLEMENTED
