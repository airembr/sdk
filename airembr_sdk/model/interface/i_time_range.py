from typing import Optional
from _datetime import timedelta
from pydantic import BaseModel
from enum import Enum


class IDatetimeType(str, Enum):
    second = 'second'
    minute = 'minute'
    hour = 'hour'
    day = 'day'
    week = 'week'
    month = 'month'
    year = 'year'


class IDateDeltaPayload(BaseModel):
    value: int
    entity: IDatetimeType

    def get_delta(self):
        entity = self.entity
        value = abs(self.value)

        if entity in ['second', 'seconds']:
            return timedelta(seconds=value)
        elif entity in ['minute', 'minutes']:
            return timedelta(minutes=value)
        elif entity in ['hour', 'hours']:
            return timedelta(hours=value)
        elif entity in ['day', 'days']:
            return timedelta(days=value)
        elif entity in ['week', 'weeks']:
            return timedelta(weeks=value)
        elif entity in ['month', 'months']:
            return timedelta(days=value * 31)
        elif entity in ['year', 'years']:
            return timedelta(days=value * 356)

        return None


class IDatetimePayload(BaseModel):
    second: Optional[int] = None
    minute: Optional[int] = None
    hour: Optional[int] = None
    date: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    meridiem: Optional[str] = None
    timeZone: int = 0

    def __str__(self):
        return "{}/{}/{} {}:{}:{} {}{}{:02d}".format(
            self.year,
            self.month,
            self.date,
            self.hour,
            self.minute,
            self.second,
            self.meridiem,
            "+" if self.timeZone >= 0 else "-",
            self.timeZone
        )


class IDatePayload(BaseModel):
    delta: Optional[IDateDeltaPayload] = None
    absolute: Optional[IDatetimePayload] = None


class IDatetimeRangePayload(BaseModel):
    minDate: Optional[IDatePayload] = None
    maxDate: Optional[IDatePayload] = None
    where: Optional[str] = ""
    timeZone: Optional[str] = None
    start: Optional[int] = 0
    limit: Optional[int] = 25
    rand: Optional[float] = 0
    sort: Optional[str] = None
