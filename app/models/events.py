from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Optional
from uuid import UUID, uuid4

from pydantic import AnyUrl, AwareDatetime, EmailStr
from sqlmodel import TIMESTAMP, Column, Field, Relationship, SQLModel
from sqlmodel import Enum as SAEnum

from app.extras.models import BaseDBModel, MutableSABaseModel

from .managers.events import EventModelManager

if TYPE_CHECKING:
    from .organizations import Organization
    from .tags import Tag


class FieldType(str, Enum):
    ATTENDEE_EMAIL = "ATTENDEE_EMAIL"
    EMAIL = "EMAIL"
    TEXT = "TEXT"
    TEXTAREA = "TEXTAREA"
    CHOICE = "CHOICE"


class AttendeeQuestion(MutableSABaseModel):
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


AttendeeQuestionSAType = AttendeeQuestion.to_sa_type(many=True)


class EventSource(str, Enum):
    EVENTTRAKKA = "EVENTTRAKKA"
    EXTERNAL = "EXTERNAL"


class EventMode(str, Enum):
    VIRTUAL = "VIRTUAL"
    PHYSICAL = "PHYSICAL"


class Currency(str, Enum):
    USD = "USD"
    NGN = "NGN"


class EventPublicationStatus(str, Enum):
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


class EventFee(MutableSABaseModel):
    amount: int = Field(default=0, ge=0)
    currency: Currency


EventFeeSAType = EventFee.to_sa_type()


class EventTag(SQLModel, table=True):
    __tablename__ = "eventtags"

    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True)
    event_id: UUID = Field(foreign_key="events.id", primary_key=True)


class Event(BaseDBModel, table=True):
    __tablename__ = "events"

    source: EventSource = Field(
        EventSource.EVENTTRAKKA, description="", sa_column=Field(SAEnum(EventSource))
    )
    organization_id: UUID | None = Field(
        foreign_key="organizations.id", ondelete="CASCADE"
    )
    organization: Optional["Organization"] = Relationship()
    status: EventPublicationStatus = Field(
        EventPublicationStatus.DRAFT,
        description="",
        sa_column=Field(SAEnum(EventPublicationStatus)),
    )
    mode_of_attending: EventMode = Field(
        description="", sa_column=Field(SAEnum(EventMode))
    )
    title: str = Field(max_length=128)
    theme: str | None = Field(max_length=128)
    description: str | None
    tags: list["Tag"] | None = Relationship(link_model=EventTag)
    fee: EventFee | None = Field(None, sa_column=Column(EventFeeSAType))
    starts_at: AwareDatetime = Field(sa_type=TIMESTAMP(timezone=True))
    ends_at: AwareDatetime | None = Field(sa_type=TIMESTAMP(timezone=True))
    location: str | None = Field(
        max_length=128,
        description="for physical events, address of the venue is required",
    )
    link: str | None = Field(
        description="for virtual events, event link is required. a physical event may also be streamed live. this applies"
    )
    # TODO: some event provide per attendee passcode. support this feature.
    passcode: str | None = Field(
        max_length=64,
        description="some virtual events may require a passcode to be able join",
    )
    attendee_questionnaire: list["AttendeeQuestion"] | None = Field(
        None,
        description="attendee questionnaire is a list of fields used to retrieve additional information from the attendees",
        sa_column=Column(AttendeeQuestionSAType),
    )

    objects: ClassVar[EventModelManager["Event"]] = EventModelManager()

    @property
    def is_free(self):
        return self.fee is None


class SocialMediaPlatform(str, Enum):
    GITHUB = "GITHUB"
    LINKED_IN = "LINKED_IN"
    X = "X"
    TWITCH = "TWITCH"
    YOUTUBE = "YOUTUBE"


class SocialAccount(MutableSABaseModel):
    platform: SocialMediaPlatform
    link: AnyUrl


class PhoneNumberInformation(MutableSABaseModel):
    country_code: str = Field("+234")
    number: str  # TODO regex for phone number
    is_hotline: bool
    is_available_on_whatsapp: bool
    is_available_on_telegram: bool


class ContactInformation(MutableSABaseModel):
    phone_numbers: list[PhoneNumberInformation]
    email_addresses: list[EmailStr]
    website: AnyUrl | None
    blog: AnyUrl | None
    social_accounts: list[SocialAccount]


ContactInformationSAType = ContactInformation.to_sa_type()


class EventOfficialType(str, Enum):
    HOST = "HOST"
    KEY_NOTE_SPEAKER = "KEY_NOTE_SPEAKER"


class EventOfficial(BaseDBModel, table=True):
    __tablename__ = "event_officials"

    event_id: UUID | None = Field(foreign_key="events.id", ondelete="CASCADE")
    type: EventOfficialType = Field(sa_column=Field(SAEnum(EventOfficialType)))
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    role: str = Field(
        max_length=128,
        description=(
            "The role of the official at the organization (e.g. OSCA Ado-EKiti Lead) or the "
            "role of the guest or keynote speaker (e.g. C.T.O at Coyote Solutions)"
        ),
    )
    contact_information: ContactInformation | None = Field(
        sa_column=Column(ContactInformationSAType)
    )
