from typing import Tuple

from airembr.system.adapter.metadata.mysql.interface import canonical_entity_dao


async def list_canonical_entities(query: str, limit: int, start: int, output: str) -> Tuple[list, int]:
    return await canonical_entity_dao.load_all_canonical_entities(query, limit=limit, start=start, output=output)


async def list_entity_properties(entity_id: str, output: str) -> dict:
    props = await canonical_entity_dao.load_properties_by_entity_id(entity_id)
    if output == 'meta':
        result = [{"id": p.id, "name": p.name} for p in props]
    else:
        result = props
    return {"total": len(result), "result": result}
