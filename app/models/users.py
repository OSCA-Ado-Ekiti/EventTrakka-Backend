from typing import ClassVar

from pydantic import EmailStr
from sqlmodel import Field

from app.core.security import get_password_hash
from app.extras.models import BaseDBModel
from app.models.managers.users import UserModelManager


class User(BaseDBModel, table=True):
    __tablename__ = "users"

    email: EmailStr = Field(max_length=320)
    password: str = Field(max_length=60)
    first_name: str | None = Field(max_length=50)
    last_name: str | None = Field(max_length=50)
    is_active: bool = Field(default=True)
    is_email_verified: bool = Field(False)

    objects: ClassVar[UserModelManager["User"]] = UserModelManager()

    async def set_password(self, new_password: str):
        update_data = {"password": get_password_hash(new_password)}
        await self.objects.update(id=self.id, update_data=update_data)
