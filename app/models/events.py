from enum import Enum
from typing import TYPE_CHECKING

from pydantic import AnyUrl, AwareDatetime, EmailStr
from sqlmodel import JSON, Field, SQLModel, String
from sqlmodel import Enum as SAEnum

from app.extras.models import BaseDBModel

if TYPE_CHECKING:
    from .tags import Tag


class EventSource(str, Enum):
    EVENTTRAKKA = "EVENTTRAKKA"
    EXTERNAL = "EXTERNAL"


class EventMode(str, Enum):
    VIRTUAL = "VIRTUAL"
    PHYSICAL = "PHYSICAL"


class EventFeeMode(str, Enum):
    FREE = "FREE"
    PAID = "PAID"


class Currency(str, Enum):
    USD = "USD"
    NGN = "NGN"


class EventFee(SQLModel):
    mode: EventFeeMode
    amount: int | None
    currency: Currency | None


class EventPublicationStatus(SQLModel):
    """
    This indicates the status of an event for public use, When an event is first created by an `Organization`,
    it is created in draft mode i.e. `EventPublicationStatus.DRAFT` which allows the `Organization` creating the
    event to further modify the `Event` if necessary. When the `Organization` is satisfied with the event, they
    can open it to the public by updating the status of the event to `EventPublicationStatus.OPEN` and when the
    event date expires the event is automatically closed by setting the status to `EventPublicationStatus.CLOSE`.
    Only `Events` that never exceeded the `DRAFT` status may be deleted from eventtrakka. opened events are archived
    instead of deleting them.
    """

    DRAFT = "DRAFT"
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    ARCHIVE = "ARCHIVE"


class Event(BaseDBModel):
    __tablename__ = "events"

    source: EventSource
    status: EventPublicationStatus
    mode_of_attending: EventMode
    title: str
    theme: str | None
    description: str | None
    tags: list[Tag] | None
    fee: EventFee
    starts_at: AwareDatetime
    ends_at: AwareDatetime | None
    location: str | None
    link: str | None


class SocialMediaPlatform(str, Enum):
    GITHUB = "GITHUB"
    LINKED_IN = "LINKED_IN"
    X = "X"
    TWITCH = "TWITCH"
    YOUTUBE = "YOUTUBE"


class SocialAccount(SQLModel):
    platform: SocialMediaPlatform
    link: AnyUrl


class PhoneNumberInformation(SQLModel):
    country_code: str = Field("+234")
    number: str  # TODO regex for phone number
    is_hotline: bool
    is_available_on_whatsapp: bool
    is_available_on_telegram: bool


class ContactInformation(SQLModel):
    phone_numbers: list[PhoneNumberInformation]
    email_addresses: list[EmailStr]
    website: AnyUrl | None
    blog: AnyUrl | None
    social_accounts: list[SocialAccount]


class EventOfficialType(str, Enum):
    HOST = "HOST"
    KEY_NOTE_SPEAKER = "KEY_NOTE_SPEAKER"


class EventOfficial(BaseDBModel):
    __tablename__ = "event_officials"

    event: Event | None = Field(foreign_key="events", ondelete="CASCADE")
    type: EventOfficialType = Field(sa_column=Field(SAEnum(EventOfficialType)))
    first_name: str = Field(sa_column=Field(String(50)))
    last_name: str = Field(sa_column=Field(String(50)))
    role: str = Field(
        description=(
            "The role of the official at the organization (e.g. OSCA Ado-EKiti Lead) or the "
            "role of the guest or keynote speaker (e.g. C.T.O at Coyote Solutions)"
        ),
        sa_column=Field(String(128)),
    )
    contact_information: ContactInformation | None = Field(
        sa_column=Field(JSON(none_as_null=True))
    )
