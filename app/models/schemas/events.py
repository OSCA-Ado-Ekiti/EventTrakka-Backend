from uuid import UUID

from pydantic import AwareDatetime, Field
from sqlmodel import SQLModel

from app.core.utils import aware_datetime_now
from app.models.events import (
    AttendeeQuestion,
    EventFee,
    EventMode,
    EventPublicationStatus,
    EventSource,
)
from app.models.tags import Tag


class CreateEvent(SQLModel):
    source: EventSource = EventSource.EVENTTRAKKA
    organization_id: UUID
    mode_of_attending: EventMode
    title: str
    theme: str | None = None
    description: str | None = None
    tags: list[UUID] | None = None
    fee: EventFee | None = None
    starts_at: AwareDatetime = Field(default_factory=aware_datetime_now)
    ends_at: AwareDatetime | None = None
    location: str | None = None
    link: str | None = None
    passcode: str | None = None
    attendee_questionnaire: list[AttendeeQuestion] | None = None


class EventPublic(SQLModel):
    mode_of_attending: EventMode
    status: EventPublicationStatus
    title: str
    theme: str | None = None
    description: str | None = None
    tags: list[Tag] | None = None
    fee: EventFee | None = None
    starts_at: AwareDatetime
    ends_at: AwareDatetime | None = None
    location: str | None = None
    link: str | None = None
    passcode: str | None = None
    attendee_questionnaire: list[AttendeeQuestion] | None = None
