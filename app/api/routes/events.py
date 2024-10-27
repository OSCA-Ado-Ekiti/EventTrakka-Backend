from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import Page

from app.api.deps import CurrentUser
from app.core.utils import ENDPOINT_NOT_IMPLEMENTED
from app.models import Event, Organization
from app.models.events import EventPublicationStatus
from app.models.organizations import OrganizationMemberPermission
from app.models.schemas.events import CreateEvent, EventPublic

router = APIRouter(prefix="/events")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(current_user: CurrentUser, data: CreateEvent):
    """Create a tech event"""
    organization = await Organization.objects.get(
        Organization.id == data.organization_id
    )
    if not organization.is_member(user=current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="organization not found"
        )
    if not organization.member_has_permission(
        OrganizationMemberPermission.MANAGE_EVENTS, user=current_user
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you don't have permissions to create an event for the organization",
        )
    return await Event.objects.create_event(data)


@router.get("/public/")
async def get_events_as_public() -> Page[EventPublic]:
    return await Event.objects.filter(
        None,
        Event.status.in_([EventPublicationStatus.OPEN, EventPublicationStatus.CLOSE]),
    )


@router.patch("/{id}/")
async def partial_update_event(id: UUID, current_user: CurrentUser):
    """Update a tech events"""
    raise ENDPOINT_NOT_IMPLEMENTED


@router.delete("/{id}/")
async def delete_event(id: UUID, current_user: CurrentUser):
    raise ENDPOINT_NOT_IMPLEMENTED


@router.get("/{id}/attendees/")
async def get_attendees(id: UUID, current_user: CurrentUser):
    """Retrieve attendees"""
    raise ENDPOINT_NOT_IMPLEMENTED
