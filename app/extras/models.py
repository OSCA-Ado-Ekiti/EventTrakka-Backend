from typing import ClassVar
from uuid import UUID, uuid4

from pydantic import AwareDatetime
from sqlmodel import TIMESTAMP, Field, SQLModel

from app.core.utils import aware_datetime_now
from app.models.managers.base_manager import BaseModelManager


class BaseDBModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: AwareDatetime = Field(
        default_factory=aware_datetime_now, sa_type=TIMESTAMP(timezone=True)
    )
    last_updated_at: AwareDatetime | None = Field(sa_type=TIMESTAMP(timezone=True))

    objects: ClassVar[BaseModelManager] = BaseModelManager()
