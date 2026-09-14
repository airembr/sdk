from typing import Optional

from airembr.model.metadata.sys_canonical_entity import CanonicalEntityProperty
from airembr.system.adapter.metadata.mysql.interface import canonical_entity_dao


async def list_entity_properties(entity_id: str, output: str) -> dict:
    props = await canonical_entity_dao.load_properties_by_entity_id(entity_id)
    if output == 'meta':
        result = [{"id": p.id, "name": p.name} for p in props]
    else:
        result = props
    return {"total": len(result), "result": result}


async def get_entity_property(prop_id: str) -> Optional[CanonicalEntityProperty]:
    return await canonical_entity_dao.load_canonical_entity_property_by_id(prop_id)


async def save_entity_property(entity_id: str, prop: CanonicalEntityProperty) -> CanonicalEntityProperty:
    prop.canonical_entity_id = entity_id
    await canonical_entity_dao.replace_canonical_entity_property(prop)
    return prop


async def delete_entity_property(prop_id: str) -> bool:
    await canonical_entity_dao.delete_canonical_entity_property_by_id(prop_id)
    return True
