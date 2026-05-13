from pydantic import BaseModel
from typing import Literal, Optional

from airembr_sdk.api.model.collection.instance import Instance


class ObjectNode(BaseModel):
    instance: Instance
    role: Optional[str] = None
    traits: Optional[dict] = None


class EventNode(BaseModel):
    type: Literal["event"]
    label: str
    traits: Optional[dict] = None


class SimplifiedObservation(BaseModel):
    actor: Optional[ObjectNode] = None
    relation: EventNode
    object: Optional[ObjectNode] = None
