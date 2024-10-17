from datetime import datetime
from uuid import UUID
from sqlmodel import Field
from typing import Optional
from pydantic import EmailStr

from app.extras.models import BaseDBModel
from app.managers import BaseModelManager


class OTPRecord(BaseDBModel):
    """OTPRecord stores the one-time passwords generated for email verification and other
    authentication purposes. Each OTP is associated with a specific user email and has an
    expiration time. The model tracks whether the OTP has been used and when it was created
    to enforce security policies and cleanup old records.
    """

    __tablename__ = "otp_records"

    email: EmailStr = Field(
        index=True,
        description="Email address associated with the OTP",
    )
    otp_code: str = Field(
        max_length=6,
        min_length=6,
        description="6-digit one-time password",
    )
    purpose: str = Field(
        default="email_verification",
        description="Purpose of the OTP (e.g., email_verification, password_reset)",
    )
    expires_at: datetime = Field(
        description="Timestamp when the OTP expires",
    )
    is_used: bool = Field(
        default=False,
        description="Flag indicating if the OTP has been used",
    )
    used_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the OTP was used",
    )
    user_id: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        description="Associated user ID if the OTP is for an existing user",
    )

    @property
    def objects(self):
        return BaseModelManager(model_class=self.__class__)
    
    @property
    def is_expired(self) -> bool:
        """Check if the OTP has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if the OTP is still valid for use."""
        return not (self.is_used or self.is_expired)
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "otp_code": "123456",
                "purpose": "email_verification",
                "expires_at": "2024-10-17T10:00:00",
                "is_used": False,
                "used_at": None,
                "user_id": None
            }
        }

IndexConfig = {
    "indexes": [
        ("email", "purpose"), 
        ("expires_at",), 
    ]
}