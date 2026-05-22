from enum import Enum
from typing import List, Optional

from airembr.model.system.named_entity import NamedEntity


class PropertyType(str, Enum):
    STRING = "STRING"
    NUMBER = "NUMBER"
    DATE = "DATE"
    REFERENCE = "REFERENCE"


class CanonicalEntityProperty(NamedEntity):
    # name (inherited) is the property identifier, e.g. "serial_number"
    type: PropertyType
    default: Optional[str] = None
    required: bool = False
    canonical_entity_id: str


class CanonicalEntity(NamedEntity):
    # name (inherited) is the canonical type label, e.g. "DEVICE", "LOCATION"
    classification: Optional[str] = None
    identification: Optional[List[str]] = None
    properties: List[CanonicalEntityProperty] = []
