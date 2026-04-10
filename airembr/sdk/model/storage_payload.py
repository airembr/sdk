from dataclasses import dataclass
from typing import List, Optional

from durable_dot_dict.dotdict import DotDict


@dataclass
class StoragePayload:
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
