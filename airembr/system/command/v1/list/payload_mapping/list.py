from typing import List, Optional
from uuid import uuid4

from airembr.model.metadata.sys_event_mapping import EventTypeMetadata
from airembr.system.adapter.metadata.mysql.interface import event_mapping_dao
from airembr.system.command.v1.errors.payload_mapping_errors import EventMappingError
from airembr.system.service.events import get_default_mappings_for


async def list_event_mappings(event_type: str) -> List[EventTypeMetadata]:
    """
    Returns a list of event type mappings both build-in and custom for given event type
    """

    mappings: List[EventTypeMetadata] = []

    build_in = get_default_mappings_for(event_type, "copy")
    if build_in is not None:
        build_in = EventTypeMetadata(**{
            'id': str(uuid4()),
            'name': 'Build in mapping',
            'event_type': event_type, 'description': f"\"{event_type}\" event mapping.",
            'enabled': True,
            'index_schema': build_in,
            'tags': ['General'],
            'build_in': True
        })
        mappings.append(build_in)

    records, total = await event_mapping_dao.load_by_event_type(event_type)

    if records:
        mappings.extend(records)
    else:
        raise EventMappingError(f"Mapping for event type [{event_type}] not found.", 404)

    return mappings


async def list_event_type_mappings_by_tag(query: str, start: Optional[int], limit: Optional[int]):
    """
    Lists event type metadata by tag, according to given start (int), limit (int) and query (str)
    """

    return await event_mapping_dao.load_all(search=query, limit=limit, offset=start)
