from typing import Optional, Tuple

from airembr.system.adapter.metadata.mysql.interface import event_reshaping_dao
from airembr.system.command.v1.errors.reshaping_schema_errors import EventReshapingError


async def get_reshape_schemas_by_event_type(event_type: str, only_enabled: bool) -> Tuple[list, int]:
    records, total = await event_reshaping_dao.load_event_reshaping_by_event_type(event_type, only_enabled)
    if not records:
        raise EventReshapingError(f"No event reshaping for event type {event_type} found.", 404)
    return records, total


async def load_reshape_schemas(limit: Optional[int], query: Optional[str]) -> Tuple[list, int]:
    return await event_reshaping_dao.load_all_event_reshaping(search=query, limit=limit)
