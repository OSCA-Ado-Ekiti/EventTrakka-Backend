from fastapi import APIRouter
from uuid import UUID

router = APIRouter(prefix="/events")


@router.post('/')
async  def create_event():
    ...

@router.get('/')
async def get_events():
    ...

@router.patch('/{id}')
async def partial_update_event(id: UUID):
    ...