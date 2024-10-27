import secrets
import string
from datetime import timedelta
from enum import Enum
from typing import ClassVar
from uuid import UUID

from pydantic import AwareDatetime
from sqlmodel import TIMESTAMP, Field
from sqlmodel import Enum as SAEnum

from app.core.config import settings
from app.core.utils import aware_datetime_now
from app.extras.models import BaseDBModel
from app.models.managers.otp import OTPRecordManager


class OTPPurpose(str, Enum):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"


def generate_otp(length: int = 6) -> str:
    characters = string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


class OTPRecord(BaseDBModel, table=True):
    """OTPRecord stores one-time passwords for email verification and authentication."""

    __tablename__ = "otp_records"

    code: str = Field(
        max_length=settings.OTP_LENGTH,
        default_factory=generate_otp,
        description="one-time password",
    )
    purpose: OTPPurpose = Field(
        description="Purpose of the OTP (e.g., email_verification, password_reset)",
        sa_column=Field(SAEnum(OTPPurpose)),
    )
    expires_at: AwareDatetime = Field(
        description="Timestamp when the OTP expires",
        default_factory=lambda: aware_datetime_now()
        + timedelta(seconds=settings.OTP_EXPIRE_MINUTES),
        sa_type=TIMESTAMP(timezone=True),
    )
    user_id: UUID | None = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        description="Associated user ID if the OTP is for an existing user",
    )

    objects: ClassVar[OTPRecordManager["OTPRecord"]] = OTPRecordManager()

    @property
    def is_expired(self) -> bool:
        """Check if the OTP has expired."""
        return aware_datetime_now() > self.expires_at
