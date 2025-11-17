from datetime import timezone

from time import time

import pytz
from _datetime import datetime, timedelta
from typing import Optional, Tuple

from pydantic import BaseModel
from enum import Enum

from sdk.airembr.common.time_parser import parse_date, parse_date_delta
from sdk.airembr.common.date import now_in_utc


class DatetimeType(str, Enum):
    second = 'second'
    minute = 'minute'
    hour = 'hour'
    day = 'day'
    week = 'week'
    month = 'month'
    year = 'year'


class DateDeltaPayload(BaseModel):
    value: int
    entity: DatetimeType

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


class DatetimePayload(BaseModel):
    second: Optional[int] = None
    minute: Optional[int] = None
    hour: Optional[int] = None
    date: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    meridiem: Optional[str] = None
    timeZone: int = 0

    @staticmethod
    def now():
        now = now_in_utc()
        return DatetimePayload(year=now.year, month=now.month, date=now.day,
                               hour=now.hour, minute=now.minute, second=now.second,
                               meridiem=now.strftime("%p"))

    @staticmethod
    def build(date: datetime) -> 'DatetimePayload':
        return DatetimePayload(year=date.year, month=date.month, date=date.day,
                               hour=date.hour, minute=date.minute, second=date.second,
                               meridiem=date.strftime("%p"))

    def is_set(self):
        return self.year is not None \
            and self.month is not None \
            and self.date is not None \
            and self.hour is not None \
            and self.minute is not None \
            and self.second is not None \
            and self.meridiem is not None

    def get_date(self) -> Optional[datetime]:
        if self.is_set():
            return datetime(year=self.year,
                            month=self.month,
                            day=self.date,
                            hour=self.hour,
                            minute=self.minute,
                            second=self.second,
                            tzinfo=timezone.utc)
        return None

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


class DatePayload(BaseModel):
    delta: Optional[DateDeltaPayload] = None
    absolute: Optional[DatetimePayload] = None

    @staticmethod
    def create(string: str) -> 'DatePayload':
        if string == 'now':
            return DatePayload()
        else:
            date = parse_date(string)
            if date is not None:
                return DatePayload(
                    absolute=DatetimePayload.build(date)
                )
            else:
                delta = parse_date_delta(string)
                if delta is not None:
                    date = datetime.fromtimestamp(time() + delta)
                    return DatePayload(
                        absolute=DatetimePayload.build(date)
                    )

        raise ValueError(f"Could not parse date {string}")

    def get_date(self) -> datetime:
        if self.absolute is None:
            absolute_date = now_in_utc()
        else:
            absolute_date = self.absolute.get_date()

            # If absolute date is None, Then use now

            if absolute_date is None:
                absolute_date = now_in_utc()

        # Get delta
        if self._is_delta_set():
            delta, sign = self._get_delta()
            return absolute_date + (sign * delta)

        return absolute_date

    def is_absolute(self):
        return self.absolute is not None and not self._is_delta_set()

    def _is_delta_set(self) -> bool:
        return self.delta is not None

    def _get_delta(self) -> Tuple[delta, int]:
        return self.delta.get_delta(), (-1 if self.delta.value < 0 else 1)

    @staticmethod
    def now() -> 'DatePayload':
        return DatePayload(absolute=DatetimePayload.now())

    @staticmethod
    def as_delta(value, unit: DatetimeType) -> 'DatePayload':
        return DatePayload(delta=DateDeltaPayload(value=value, entity=unit))


class DatetimeRangePayload(BaseModel):
    minDate: Optional[DatePayload] = None
    maxDate: Optional[DatePayload] = None
    where: Optional[str] = ""
    timeZone: Optional[str] = None
    start: Optional[int] = 0
    limit: Optional[int] = 25
    rand: Optional[float] = 0
    sort: Optional[str] = None

    def get_dates(self) -> Tuple[datetime, datetime]:

        if self._is_not_set(self.minDate):
            self.minDate = DatePayload(
                absolute=DatetimePayload(year=1970, month=1, hour=0, minute=0, second=0, date=1, meridiem="AM"))

        if self._is_not_set(self.maxDate):
            self.maxDate = DatePayload(absolute=DatetimePayload.now())

        min_date = self.minDate.get_date()
        max_date = self.maxDate.get_date()

        if min_date > max_date:
            raise ValueError(
                f"Incorrect time range. From date `{min_date}` is earlier then to date `{max_date}`.")

        return min_date, max_date

    def _is_not_set(self, date: DatePayload):
        return date is None or (date.absolute is None and date.delta is None)

    @staticmethod
    def convert_to_local_datetime(utc_datetime, timezone) -> Tuple[datetime, Optional[str]]:
        try:
            local_tz = pytz.timezone(timezone)
            local_dt = utc_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            return local_tz.normalize(local_dt), timezone  # .normalize might be unnecessary
        except pytz.exceptions.UnknownTimeZoneError:
            # todo log error
            return utc_datetime, None
