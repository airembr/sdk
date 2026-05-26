from typing import Optional, List, Tuple

from airembr.model.metadata.sys_ontology import Ontology
from airembr.system.adapter.metadata.mysql.interface.dao.canonical_entity import (
    load_canonical_entities_by_ontology_id,
)
from airembr.system.adapter.metadata.mysql.mapping.ontology_mapping import map_to_ontology
from airembr.system.adapter.metadata.mysql.service.ontology_service import OntologyService

_service = OntologyService()


async def load_ontology_by_id(ontology_id: str) -> Optional[Ontology]:
    record = await _service.load_by_id(ontology_id)
    if not record.exists():
        return None
    return record.map_to_object(map_to_ontology)


async def load_all_ontologies(query=None, limit=None, start=None, output='entity') -> Tuple[List, int]:
    records = await _service.load_all(search=query, limit=limit, offset=start)
    if not records.exists():
        return [], 0
    if output == 'meta':
        return records.as_named_entities(), records.count()
    ontologies = list(records.map_to_objects(map_to_ontology))
    if output == 'aggregate':
        for ontology in ontologies:
            ontology.canonical_entities = await load_canonical_entities_by_ontology_id(ontology.id)
    return ontologies, records.count()


async def insert_ontology(ontology: Ontology):
    return await _service.insert(ontology)


async def delete_ontology_by_id(ontology_id: str):
    await _service.delete_by_id(ontology_id)
