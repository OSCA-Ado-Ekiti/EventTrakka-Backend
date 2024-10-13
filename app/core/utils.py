from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings


def aware_datetime_now() -> datetime:
    """Returns a timezone of the current time with additional timezone info"""
    return datetime.now(tz=ZoneInfo(settings.TIMEZONE))
