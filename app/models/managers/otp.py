from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.managers.base_manager import BaseModelManager

if TYPE_CHECKING:
    from app.models.otp import OTPPurpose, OTPRecord


class OTPRecordManager[T: OTPRecord](BaseModelManager):
    """Manager class for handling OTP-related database operations."""

    async def create_otp(
        self,
        user_id: UUID,
        purpose: "OTPPurpose",
        session: AsyncSession | None = None,
    ) -> "OTPRecord":
        creation_data = {
            "purpose": purpose,
            "user_id": user_id,
        }

        return await super().create(creation_data=creation_data, session=session)
