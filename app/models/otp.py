import secrets
import string
from datetime import timedelta
from enum import Enum
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import TIMESTAMP, Field, String
from sqlmodel import Enum as SAEnum

from app.core.config import settings
from app.core.utils import aware_datetime_now
from app.extras.models import BaseDBModel
from app.managers import BaseModelManager


class OTPPurpose(str, Enum):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"


class OTPRecordManager(BaseModelManager):
    """Manager class for handling OTP-related database operations."""

    async def create_otp(
        self,
        user_id: UUID,
        purpose: OTPPurpose,
        session: AsyncSession | None = None,
    ) -> BaseDBModel:
        creation_data = {
            "purpose": purpose,
            "user_id": user_id,
        }

        return await super().create(creation_data=creation_data, session=session)


def generate_otp(length: int = 6) -> str:
    characters = string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


class OTPRecord(BaseDBModel, table=True):
    """OTPRecord stores one-time passwords for email verification and authentication."""

    __tablename__ = "otp_records"

    code: str = Field(
        sa_column=Field(String(settings.OTP_LENGTH)),
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

    @classmethod
    @property
    def objects(cls):
        return OTPRecordManager(model_class=cls)

    @property
    def is_expired(self) -> bool:
        """Check if the OTP has expired."""
        return aware_datetime_now() > self.expires_at


class OTPAlreadyExistError(Exception): ...
