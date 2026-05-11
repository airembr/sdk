from datetime import datetime
from typing import Optional, List, Literal, Any
from pydantic import BaseModel
from airembr.sdk.common.date import now_in_utc
from airembr.model.system.named_entity import NamedEntityInContext


class TimeConstraint(BaseModel):
    field: str = 'metadata_time_create'
    start: Optional[datetime] = now_in_utc(delay=-60 * 60 * 24 * 30)  # 1 month
    end: Optional[datetime] = now_in_utc()


class Actor(BaseModel):
    type: str
    where: Optional[str] = None


class Step(BaseModel):
    exists: bool
    type: Optional[str] = 'event'
    label: str
    next_in_sequence: Optional[int] = None
    where: Optional[str] = None
    within_start: Optional[int] = 0
    within_end: Optional[int] = 0
    within_unit: Optional[Literal["second", "minute", "hour", "day", "month"]] = 'day'

    def has_time_window(self):
        return self.within_end > 0 and self.within_start <= self.within_end


class EntitySegment(NamedEntityInContext):
    description: Optional[str] = ""
    tags: List[str] = []
    enabled: Optional[bool] = False
    ts: Optional[datetime] = now_in_utc()
    time: Optional[TimeConstraint] = TimeConstraint()
    entity_type: str
    entity_where: Optional[str] = None

    sequence: Optional[List[Step]] = []

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.sequence is None:
            self.sequence = []
