from app.enums import UserType
from app.extras.models import BaseDBModel
from app.managers import BaseModelManager
from pydantic import EmailStr


class User(BaseDBModel):
    __tablename__ = "users"

    type: UserType
    email: EmailStr
    password: str
    first_name: str | None
    last_name: str | None
    avatar_url: str | None

    @property
    def objects(self):
        return BaseModelManager(model_class=self.__class__)

