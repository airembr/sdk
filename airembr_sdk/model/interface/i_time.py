from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

from airembr_sdk.core.date import now_in_utc, add_utc_time_zone_if_none


class ITime(BaseModel):
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

