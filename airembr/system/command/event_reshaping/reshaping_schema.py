from typing import Optional, Tuple

from airembr.model.metadata.sys_evt_reshaping import EventReshapingSchema
from airembr.system.adapter.metadata.mysql.interface import event_reshaping_dao
from airembr.system.command.event_reshaping.errors import EventReshapingError


async def add_reshape_schema(data: EventReshapingSchema):
    await event_reshaping_dao.insert_event_reshaping(data)


async def delete_reshape_schema(reshaping_id: str):
    return await event_reshaping_dao.delete_event_reshaping_by_id(reshaping_id)


async def get_reshape_schema(reshaping_id: str) -> EventReshapingSchema:
    record = await event_reshaping_dao.load_event_reshaping_by_id(reshaping_id)
    if not record:
        raise EventReshapingError(f"No event reshaping with ID {reshaping_id} found.", 404)
    return record


async def get_reshape_schemas_by_event_type(event_type: str, only_enabled: bool) -> Tuple[list, int]:
    records, total = await event_reshaping_dao.load_event_reshaping_by_event_type(event_type, only_enabled)
    if not records:
        raise EventReshapingError(f"No event reshaping for event type {event_type} found.", 404)
    return records, total


async def load_reshape_schemas(limit: Optional[int], query: Optional[str]) -> Tuple[list, int]:
    return await event_reshaping_dao.load_all_event_reshaping(search=query, limit=limit)
