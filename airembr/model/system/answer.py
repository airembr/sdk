from typing import Optional, List

from pydantic import BaseModel

class Answer(BaseModel):
    query: str
    eql: Optional[str] = None
    answer: Optional[str] = None
    memory: Optional[dict] = {}
    entity_tolerance: int
    traits_tolerance: int
