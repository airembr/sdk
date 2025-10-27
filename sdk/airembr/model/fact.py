from datetime import datetime
from typing import Optional, List, Set

from pydantic import BaseModel

from sdk.airembr.model.entity import Entity


class EntityObject(Entity):
    pk: str
    type: str
    role: Optional[str] = None
    is_a: Optional[str] = None
    part_of: Optional[str] = None
    kind_of: Optional[str] = None
    traits: Optional[dict] = {}
    data_hash: int


class Metadata(BaseModel):
    insert: datetime = None
    create: datetime = None
    update: Optional[datetime] = None


class Semantic(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None

    def format(self, inline: bool = False):
        if inline:
            join = ": "
        else:
            join = "\n"

        if self.summary and self.description:
            return f"{self.summary}{join}{self.description}"
        if self.summary:
            return self.summary
        else:
            return self.description




class Event(Entity):
    type: str
    label: str
    traits: Optional[dict] = {}

    metadata: Metadata
    object: Optional[EntityObject] = None

    semantic: Optional[Semantic] = Semantic()


class Fact(BaseModel):
    actor: EntityObject
    sessions: Optional[Set[str]] = set()
    sources: Optional[Set[str]] = set()
    aspects: Optional[Set[str]] = set()
    events: Optional[List[Event]] = []

    context: Optional[List[EntityObject]] = None
