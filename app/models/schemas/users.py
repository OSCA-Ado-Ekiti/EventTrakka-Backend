from typing import Self

from pydantic import BaseModel, EmailStr, model_validator


class CreateUser(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("passwords do not match")
        return self


class UserPublic(BaseModel):
    email: EmailStr
    first_name: str | None
    last_name: str | None
    is_active: bool
