from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.managers.base_manager import BaseModelManager

if TYPE_CHECKING:
    from app.models.users import User


class UserModelManager[T: User](BaseModelManager):
    async def create_user(
        self,
        email: EmailStr,
        password: str,
        first_name: str | None,
        last_name: str | None,
        is_active=True,
        is_email_verified=False,
        session: AsyncSession | None = None,
    ) -> "User":
        creation_data = {
            "email": email,
            "password": get_password_hash(password),
            "first_name": first_name,
            "last_name": last_name,
            "is_active": is_active,
            "is_email_verified": is_email_verified,
        }
        try:
            user = await self.get(session, self.model_class.email == email)
        except self.model_class.DoesNotExist:
            user = None
        if user:
            raise self.model_class.AlreadyExist("user with this email already exist")
        return await super().create(creation_data=creation_data, session=session)

    async def authenticate(
        self, email: EmailStr, password: str, session: AsyncSession | None = None
    ) -> Optional["User"]:
        try:
            user = await self.get(session, self.model_class.email == email)
        except self.model_class.DoesNotExist:
            return None
        if not verify_password(password, user.password):
            return None
        return user
