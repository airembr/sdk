from typing import Optional

from pydantic import BaseModel


class TimeStats(BaseModel):
    entity_search: Optional[float] = 0
    hyper_edge_search: Optional[float] = 0
    entity_extraction: Optional[float] = 0
    context_search: Optional[float] = 0
    fact_search: Optional[float] = 0

class MemoryResponse(BaseModel):
    text: str
    stats: TimeStats