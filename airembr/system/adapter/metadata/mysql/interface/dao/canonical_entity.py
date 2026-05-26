from typing import List, Optional, Tuple

from airembr.model.metadata.sys_canonical_entity import CanonicalEntity, CanonicalEntityProperty
from airembr.system.adapter.metadata.mysql.mapping.canonical_entity_mapping import (
    map_to_canonical_entity,
    map_to_canonical_entity_property,
)
from airembr.system.adapter.metadata.mysql.service.canonical_entity_service import (
    CanonicalEntityService,
    CanonicalEntityPropertyService,
)

ces = CanonicalEntityService()
ceps = CanonicalEntityPropertyService()


async def load_canonical_entity_by_id(entity_id: str) -> Optional[CanonicalEntity]:
    record = await ces.load_by_id(entity_id)
    if not record.exists():
        return None
    entity = record.map_to_object(map_to_canonical_entity)
    entity.properties = await load_properties_by_entity_id(entity_id)
    return entity


async def load_canonical_entity_by_name(entity_name: str) -> Optional[CanonicalEntity]:
    record = await ces.load_by_name(entity_name)
    if not record.exists():
        return None
    return record.map_first_to_object(map_to_canonical_entity)


async def load_all_canonical_entities(query=None, limit=None, start=None, output='entity') -> Tuple[List, int]:
    records = await ces.load_all(search=query, limit=limit, offset=start)
    if not records.exists():
        return [], 0
    if output == 'meta':
        return records.as_named_entities(), records.count()
    entities = list(records.map_to_objects(map_to_canonical_entity))
    if output == 'aggregate':
        for entity in entities:
            entity.properties = await load_properties_by_entity_id(entity.id)
    return entities, records.count()


async def insert_canonical_entity(entity: CanonicalEntity):
    await ces.insert(entity)
    for prop in entity.properties:
        await ceps.insert(prop)


async def replace_canonical_entity(entity: CanonicalEntity):
    await ces.replace(entity)
    await ceps.delete_by_entity_id(entity.id)
    for prop in entity.properties:
        await ceps.replace(prop)


async def delete_canonical_entity_by_id(entity_id: str):
    await ceps.delete_by_entity_id(entity_id)
    await ces.delete_by_id(entity_id)


async def load_canonical_entities_by_ontology_id(ontology_id: str) -> List[CanonicalEntity]:
    records = await ces.load_by_ontology_id(ontology_id)
    if not records.exists():
        return []
    return list(records.map_to_objects(map_to_canonical_entity))


async def delete_canonical_entities_by_ontology_id(ontology_id: str):
    entities = await load_canonical_entities_by_ontology_id(ontology_id)
    for entity in entities:
        await ceps.delete_by_entity_id(entity.id)
    await ces.delete_by_ontology_id(ontology_id)


async def load_properties_by_entity_id(entity_id: str) -> List[CanonicalEntityProperty]:
    records = await ceps.load_by_entity_id(entity_id)
    if not records.exists():
        return []
    return list(records.map_to_objects(map_to_canonical_entity_property))


async def load_canonical_entity_property_by_id(prop_id: str) -> Optional[CanonicalEntityProperty]:
    record = await ceps.load_by_id(prop_id)
    if not record.exists():
        return None
    return record.map_to_object(map_to_canonical_entity_property)


async def replace_canonical_entity_property(prop: CanonicalEntityProperty):
    await ceps.replace(prop)


async def delete_canonical_entity_property_by_id(prop_id: str):
    await ceps.delete_by_id(prop_id)
