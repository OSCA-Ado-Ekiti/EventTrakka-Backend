from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.extras.models import BaseDBModel
from app.managers import BaseModelManager


class UserModelManager(BaseModelManager):
    async def create_user(
        self,
        email: EmailStr,
        password: str,
        first_name: str | None,
        last_name: str | None,
        is_active=True,
        is_email_verified=False,
        session: AsyncSession | None = None,
    ) -> BaseModel:
        creation_data = {
            "email": email,
            "password": get_password_hash(password),
            "first_name": first_name,
            "last_name": last_name,
            "is_active": is_active,
            "is_email_verified": is_email_verified,
        }
        return await super().create(creation_data=creation_data, session=session)

    async def authenticate(
        self, email: EmailStr, password: str, session: AsyncSession | None = None
    ) -> BaseModel | None:
        user = await self.get(session, self.model_class.email == email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user


class User(BaseDBModel, table=True):
    __tablename__ = "users"

    email: EmailStr
    password: str
    first_name: str | None
    last_name: str | None
    is_active: bool = Field(default=True)
    is_email_verified: bool = Field(False)

    @classmethod
    @property
    def objects(cls):
        return UserModelManager(model_class=cls)

    async def set_password(self, new_password: str):
        update_data = {"password": get_password_hash(new_password)}
        await self.objects.update(id=self.id, update_data=update_data)
