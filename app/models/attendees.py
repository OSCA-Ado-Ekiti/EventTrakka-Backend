from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
from app.extras.models import BaseDBModel
from app.managers import BaseModelManager

class Attendee(BaseDBModel):
    __tablename__ = "attendees"

    event_id: int = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    status: str = Column(String(50), default="pending")  # RSVP status (status can be pending, confirmed, etc.)
    checked_in: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    @property
    def objects(self):
        return BaseModelManager(model_class=self.__class__)
