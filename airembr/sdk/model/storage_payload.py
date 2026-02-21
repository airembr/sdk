from dataclasses import dataclass
from typing import List, Optional

from durable_dot_dict.dotdict import DotDict


@dataclass
class StoragePayload:
    fact: dict
    relation: dict
    context: List[DotDict|dict]
    timer: Optional[dict] = None
    trace_id: Optional[str] = None