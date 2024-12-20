from sqlmodel import Field

from app.extras.models import BaseDBModel


class Tag(BaseDBModel, table=True):
    __tablename__ = "tags"

    value: str = Field(
        max_length=32,
        description="The tag content. (e.g. `#HacktoberFest2024`, `OSCAFest`)",
        unique=True,
    )
