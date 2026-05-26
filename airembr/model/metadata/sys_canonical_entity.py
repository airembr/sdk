from enum import Enum
from typing import List, Optional

from airembr.model.system.named_entity import NamedEntityInContext


class PropertyType(str, Enum):
    STRING = "STRING"
    NUMBER = "NUMBER"
    DATE = "DATE"
    REFERENCE = "REFERENCE"


class CanonicalEntityProperty(NamedEntityInContext):
    # name (inherited) is the property identifier, e.g. "serial_number"
    type: PropertyType
    default: Optional[str] = None
    required: bool = False
    canonical_entity_id: Optional[str] = None


class CanonicalEntity(NamedEntityInContext):
    # name (inherited) is the canonical type label, e.g. "DEVICE", "LOCATION"
    ontology_id: str
    classification: Optional[str] = None
    identification: Optional[List[str]] = None
    properties: List[CanonicalEntityProperty] = []
