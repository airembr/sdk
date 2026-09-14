from typing import Optional, Tuple

from airembr.model.metadata.sys_canonical_entity import CanonicalEntity
from airembr.system.adapter.metadata.mysql.interface import canonical_entity_dao


async def list_canonical_entities(query: str, limit: int, start: int, output: str) -> Tuple[list, int]:
    return await canonical_entity_dao.load_all_canonical_entities(query, limit=limit, start=start, output=output)


async def get_canonical_entity(entity_id: str) -> Optional[CanonicalEntity]:
    return await canonical_entity_dao.load_canonical_entity_by_id(entity_id)


async def save_canonical_entity(entity: CanonicalEntity) -> CanonicalEntity:
    await canonical_entity_dao.replace_canonical_entity(entity)
    return entity


async def delete_canonical_entity(entity_id: str) -> bool:
    await canonical_entity_dao.delete_canonical_entity_by_id(entity_id)
    return True
