from sqlmodel import SQLModel


class CreateOrganization(SQLModel):
    name: str
    about: str | None
