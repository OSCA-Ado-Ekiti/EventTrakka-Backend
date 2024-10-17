from sqlmodel import Field

from app.extras.models import BaseDBModel


class Tag(BaseDBModel):
    value: str = Field(
        description="The tag content. (e.g. `#HacktoberFest2024`, `OscaFest`)",
        unique=True,
    )
