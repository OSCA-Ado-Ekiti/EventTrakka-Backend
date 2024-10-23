from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import JSON, Field, Relationship, SQLModel

from app.extras.models import BaseDBModel

if TYPE_CHECKING:
    from .events import Event


class FieldType(str, Enum):
    ATTENDEE_EMAIL = "ATTENDEE_EMAIL"
    EMAIL = "EMAIL"
    TEXT = "TEXT"
    TEXTAREA = "TEXTAREA"
    CHOICE = "CHOICE"


class AttendeeQuestion(SQLModel):
    id: UUID = Field(default_factory=uuid4)
    is_required: bool = Field(True, description="is the field a required field")
    label: str = Field(
        description="what to show in the form as the question label. e.g. Email Address:, Event Expectation:"
    )
    field_type: FieldType = Field(
        description=(
            "this determines how the field should be rendered in the frontend,"
            " for ATTENDEE_EMAIL, the value is match with the email field of the"
            " attendee model and does not need to be rendered in the frontend as"
            " email is always required weather an event requires a questionnaire or not"
        )
    )
    choices: list[str] | None = Field(None)
    allow_multiple_choices: bool = Field(
        False,
        description="when the field type is a CHOICE, should the submission allow",
    )


class Attendee(BaseDBModel):
    """Attendee is a representation of users that RSVP an `Event` (tech event) created by an
    `Organization` (tech communities). Even though Attendees are real word users of the platform,
    they're not `User` on Eventtrakka which is limited to admin and `Organization` members for
    the sake of simplicity and may be changed in the future. Ateendees also do not need to be
    signed in. They just surf Eventtrakka for `Event`s that interests them and RSVP the event
    by filling up a from which results in the creation of this model.
    """

    __tablename__ = "attendees"

    event_id: UUID = Field(
        foreign_key="events.id",
        ondelete="CASCADE",
        description="The event the attendee RSVP",
    )
    event: "Event" = Relationship()
    attended_event: bool = Field(
        False,
        description="An event may be virtual or physical, this flag helps to indicate if the user attended the event",
    )
    email: EmailStr = Field(max_length=320)
    questionnaire_submission: dict | None = Field(
        sa_type=JSON(none_as_null=True),
    )
