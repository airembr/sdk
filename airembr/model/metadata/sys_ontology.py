from typing import Optional, List, TYPE_CHECKING

from airembr.model.system.named_entity import NamedEntityInContext

if TYPE_CHECKING:
    from airembr.model.metadata.sys_canonical_entity import CanonicalEntity


class Ontology(NamedEntityInContext):
    url: Optional[str] = None
    canonical_entities: List = []
