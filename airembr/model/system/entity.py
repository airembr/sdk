from pydantic import BaseModel
from typing import Optional, List
from uuid import uuid4

from airembr.model.system.time import Time


class Entity(BaseModel):
    id: str

    @staticmethod
    def new() -> 'Entity':
        return Entity(id=str(uuid4()))

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id if isinstance(other, Entity) else False


class PrimaryEntity(Entity):
    primary_id: Optional[str] = None
    metadata: Optional[Time] = None
    ids: Optional[List[str]] = None
