from typing import Optional, Tuple

from airembr.system.adapter.metadata.mysql.interface import event_validation_dao


async def load_validators(limit: int, query: Optional[str]) -> Tuple[list, int]:
    return await event_validation_dao.load_all(search=query, limit=limit)
