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


class Event(Entity):
    type: str
    label: str
    traits: Optional[dict] = {}

    metadata: Metadata
    object: Optional[EntityObject] = None


class Fact(BaseModel):
    actor: EntityObject
    sessions: Optional[Set[str]] = set()
    sources: Optional[Set[str]] = set()
    aspects: Optional[Set[str]] = set()
    events: Optional[List[Event]] = []

    context: Optional[List[EntityObject]] = None
