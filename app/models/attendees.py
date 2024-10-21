from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field

from app.extras.models import BaseDBModel


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
        foreign_key="events",
        ondelete="CASCADE",
        description="The event the attendee RSVP",
    )
    attended_event: bool = Field(
        False,
        description="An event may be virtual or physical, this flag helps to indicate if the user attended the event",
    )
    email: EmailStr
