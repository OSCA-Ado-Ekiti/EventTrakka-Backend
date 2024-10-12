from fastapi import APIRouter

router = APIRouter(prefix="/attendee")


@router.post("/")
async def create_attendee():
    """Create an attendees.

    Attendees are users who sign up for an event
    """
    ...


@router.get("/")
async def get_attendees():
    """Retrieve attendees"""
    ...
