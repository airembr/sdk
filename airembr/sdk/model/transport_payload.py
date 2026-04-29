from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from durable_dot_dict.dotdict import DotDict


@dataclass
class FactTransportPayload:
    source_id: str
    observation: dict
    fact: dict
    relation: dict
    context: List[DotDict|dict]
    gids: List[DotDict|dict]
    description: Optional[str] = None
    summary: Optional[str] = None
    timer: Optional[dict] = None
    trace_id: Optional[str] = None
    session: Optional[dict] = None

    def has_relation(self) -> bool:
        return bool(self.fact) and bool(self.relation)

@dataclass
class ObsTransportPayload:
    id: str
    source_id: str
    entities: int
    label: Optional[str] = None
    session_id: Optional[str] = None
    description: Optional[str] = None
    metadata_time_insert: Optional[datetime] = None
    metadata_time_create: Optional[datetime] = None