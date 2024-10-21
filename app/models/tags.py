from sqlmodel import Field

from app.extras.models import BaseDBModel


class Tag(BaseDBModel):
    __tablename__ = "tags"

    value: str = Field(
        description="The tag content. (e.g. `#HacktoberFest2024`, `OSCAFest`)",
        unique=True,
    )
