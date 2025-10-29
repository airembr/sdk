from datetime import datetime
from typing import Optional, List

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

    def to_string(self, actor):
        actor_traits_str = _format_traits(getattr(actor, "traits", {}))

        semantic_desc = self.semantic.to_string(inline=True) if self.semantic else ""
        object = self.object
        if object:
            object_traits_str = _format_traits(getattr(object, "traits", {}))
            object_type = f"{object.type} ({object_traits_str})"
        else:
            object_type = ""

        if semantic_desc:
            semantic_desc = f"\nDetails: {semantic_desc}"
        else:
            semantic_desc = ""

        return f"Fact: {actor.type} ({actor_traits_str}) {self.label} {object_type}{semantic_desc}"


class FlatFactObservation(BaseModel):
    actor: EntityObject
    session: Entity
    source: Entity
    aspect: Optional[str] = None
    relation: Relation

    context: Optional[List[EntityObject]] = None
