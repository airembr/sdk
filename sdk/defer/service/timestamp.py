from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def now_in_utc(delay=None) -> datetime:
    now = datetime.utcnow().replace(tzinfo=ZoneInfo('UTC'))

    if delay is None:
        return now

    return now + timedelta(seconds=delay)