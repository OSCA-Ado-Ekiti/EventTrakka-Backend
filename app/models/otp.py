from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import Optional
from sqlmodel import Field, String
from pydantic import EmailStr
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.extras.models import BaseDBModel
from app.managers import BaseModelManager


class OTPRecordManager(BaseModelManager):
    """Manager class for handling OTP-related database operations."""

    async def create_otp_record(
        self,
        email: EmailStr,
        otp_code: str,
        purpose: str = "email_verification",
        expires_at: datetime = datetime.now(
            timezone.utc) + timedelta(minutes=10),
        session: AsyncSession | None = None,
        user_id: Optional[UUID] = None,
    ) -> BaseDBModel:
        creation_data = {
            "email": email,
            "otp_code": otp_code,
            "purpose": purpose,
            "expires_at": expires_at,
            "user_id": user_id,
            "is_used": False,
        }

        return await super().create(creation_data=creation_data, session=session)

    async def get_active_otp(
        self, email: EmailStr, purpose: str, session: AsyncSession | None = None
    ) -> BaseDBModel | None:
        """Fetch the latest active OTP record for a given email and purpose."""
        otp_record = await self.get(
            session,
            self.model_class.email == email,
            self.model_class.purpose == purpose,
            self.model_class.is_used == False,
            self.model_class.expires_at > datetime.now(timezone.utc)
        )
        return otp_record


class OTPRecord(BaseDBModel, table=True):
    """OTPRecord stores one-time passwords for email verification and authentication."""

    __tablename__ = "otp_records"

    email: EmailStr = Field(index=True, description="Email address associated with the OTP")
    otp_code: str = Field(sa_column=Field(String(6)), description="6-digit one-time password")
    purpose: str = Field(default="email_verification", description="Purpose of the OTP (e.g., email_verification, password_reset)")
    expires_at: datetime = Field(description="Timestamp when the OTP expires")
    is_used: bool = Field(default=False, description="Flag indicating if the OTP has been used")
    used_at: Optional[datetime] = Field(default=None, description="Timestamp when the OTP was used")
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id", description="Associated user ID if the OTP is for an existing user")

    @classmethod
    @property
    def objects(cls):
        return OTPRecordManager(model_class=cls)

    @property
    def is_expired(self) -> bool:
        """Check if the OTP has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the OTP is valid (not used and not expired)."""
        return not (self.is_used or self.is_expired)


class OTPAlreadyExistError(Exception):
    ...
