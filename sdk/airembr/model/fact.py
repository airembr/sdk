from datetime import datetime
from typing import Optional, List
from durable_dot_dict.dotdict import DotDict

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


class Metadata(BaseModel):
    insert: datetime = None
    create: datetime = None
    update: Optional[datetime] = None


class Semantic(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None

    def to_string(self, inline: bool = False):
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


class Relation(Entity):
    type: str
    label: str
    traits: Optional[dict] = {}

    metadata: Metadata
    object: Optional[EntityObject] = None

    semantic: Optional[Semantic] = Semantic()


class Fact(BaseModel):
    actor: EntityObject
    session: Entity
    source: Entity
    aspect: Optional[str] = None
    relation: Relation

    context: Optional[List[EntityObject]] = None


class DotDictFact(DotDict):

    def to_fact(self):
        return Fact(**self.root)
