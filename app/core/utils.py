from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status

from app.core.config import settings


def aware_datetime_now() -> datetime:
    """Returns a timezone of the current time with additional timezone info"""
    return datetime.now(tz=ZoneInfo(settings.TIMEZONE))


ENDPOINT_NOT_IMPLEMENTED = HTTPException(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    detail="endpoint has not been implemented yet",
)
