from fastapi import APIRouter

from app.core.utils import ENDPOINT_NOT_IMPLEMENTED

router = APIRouter(prefix="/event-officials")


@router.post("/")
async def create_event_officials():
    raise ENDPOINT_NOT_IMPLEMENTED


@router.get("/")
async def get_event_officials():
    raise ENDPOINT_NOT_IMPLEMENTED


@router.put("/{id}/")
async def update_event_officials():
    raise ENDPOINT_NOT_IMPLEMENTED


@router.delete("/{id}/")
async def delete_event_official():
    raise ENDPOINT_NOT_IMPLEMENTED
