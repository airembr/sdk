from typing import Optional

from airembr.model.metadata.sys_canonical_entity import CanonicalEntity
from airembr.system.adapter.metadata.mysql.interface import canonical_entity_dao


async def get_canonical_entity(entity_id: str) -> Optional[CanonicalEntity]:
    return await canonical_entity_dao.load_canonical_entity_by_id(entity_id)


async def save_canonical_entity(entity: CanonicalEntity) -> CanonicalEntity:
    await canonical_entity_dao.replace_canonical_entity(entity)
    return entity


async def delete_canonical_entity(entity_id: str) -> bool:
    await canonical_entity_dao.delete_canonical_entity_by_id(entity_id)
    return True
