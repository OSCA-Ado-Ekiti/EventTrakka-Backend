from fastapi import APIRouter

router = APIRouter(prefix="/attendee")

@router.post('/')
async def create_attendee():
    ...


@router.get('/')
async def get_attendees():
    ...