from uuid import UUID, uuid4

from pydantic import AwareDatetime
from sqlmodel import TIMESTAMP, Field, SQLModel

from app.core.utils import aware_datetime_now


class BaseDBModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_on: AwareDatetime = Field(
        default_factory=aware_datetime_now, sa_type=TIMESTAMP(timezone=True)
    )
    last_updated_on: AwareDatetime | None = Field(sa_type=TIMESTAMP(timezone=True))
