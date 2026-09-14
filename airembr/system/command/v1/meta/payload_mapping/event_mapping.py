from typing import Optional

from airembr.model.metadata.sys_event_mapping import EventTypeMetadata
from airembr.system.adapter.metadata.mysql.interface import event_mapping_dao
from airembr.system.command.v1.errors.payload_mapping_errors import EventMappingError


async def add_event_type_mapping(event_mapping: EventTypeMetadata):
    """
    Creates new event type mapping in database
    """
    return await event_mapping_dao.insert(event_mapping)


async def get_event_mapping_by_id(event_type_id: str) -> Optional[EventTypeMetadata]:
    """
    Return custom event type mapping for given event type
    """
    record = await event_mapping_dao.load_by_id(event_type_id)

    if not record:
        raise EventMappingError(f"Mapping for event type [{event_type_id}] not found.", 404)

    return record


async def del_event_type_metadata(event_type_id: str):
    """
    Deletes event type metadata for given event type
    """

    return await event_mapping_dao.delete_by_id(event_type_id)
