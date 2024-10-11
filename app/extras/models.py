from datetime import datetime
from uuid import uuid4, UUID
from sqlmodel import SQLModel, Field

class BaseDBModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_on: datetime
    last_updated_on: datetime