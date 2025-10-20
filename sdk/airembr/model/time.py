from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

from sdk.airembr.service.time.time import now_in_utc, add_utc_time_zone_if_none


class Time(BaseModel):
    insert: Optional[datetime] = None
    create: Optional[datetime] = None
    update: Optional[datetime] = None

    def __init__(self, **data: Any):
        if 'insert' not in data:
            data['insert'] = now_in_utc()
        if 'create' not in data:
            if 'insert' in data:
                data['create'] = data['insert']
            else:
                data['create'] = now_in_utc()

        super().__init__(**data)

        self.insert = add_utc_time_zone_if_none(self.insert)
        self.create = add_utc_time_zone_if_none(self.create)
        self.update = add_utc_time_zone_if_none(self.update)



class ProfileVisit(BaseModel):
    last: Optional[datetime] = None
    current: Optional[datetime] = None
    count: int = 0
    tz: Optional[str] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.last = add_utc_time_zone_if_none(self.last)
        self.current = add_utc_time_zone_if_none(self.current)


class ProfileTime(Time):
    segmentation: Optional[datetime] = None
    # Inherits from Time
    visit: ProfileVisit = ProfileVisit()


class EventTime(Time):
    process_time: Optional[float] = 0
    total_time: Optional[float] = 0

