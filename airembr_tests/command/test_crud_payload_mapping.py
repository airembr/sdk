import asyncio
from uuid import uuid4

import pytest

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_event_mapping import EventTypeMetadata
from airembr.system.command.v1.errors.payload_mapping_errors import EventMappingError
from airembr.system.command.v1.meta.payload_mapping.event_mapping import (
    add_event_type_mapping,
    get_event_mapping_by_id,
    del_event_type_metadata,
)


def _make_event_mapping(event_type: str) -> EventTypeMetadata:
    # __init__ overwrites id with event_type, so the mapping's id is event_type.
    return EventTypeMetadata(name="Test Mapping", event_type=event_type, entity_type="person")


def test_crud_payload_mapping_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            event_type = f"test-payload-mapping-{uuid4()}"
            await add_event_type_mapping(_make_event_mapping(event_type))

            fetched = await get_event_mapping_by_id(event_type)

            assert fetched is not None
            assert fetched.id == event_type
            assert fetched.name == "Test Mapping"
        asyncio.run(scenario())


def test_crud_payload_mapping_delete():
    with ServerContext(Context()):
        async def scenario():
            event_type = f"test-payload-mapping-{uuid4()}"
            await add_event_type_mapping(_make_event_mapping(event_type))

            await del_event_type_metadata(event_type)

            with pytest.raises(EventMappingError):
                await get_event_mapping_by_id(event_type)
        asyncio.run(scenario())


def test_crud_payload_mapping_get_missing_raises_404():
    with ServerContext(Context()):
        async def scenario():
            with pytest.raises(EventMappingError) as exc_info:
                await get_event_mapping_by_id(f"test-payload-mapping-{uuid4()}")
            assert exc_info.value.status_code == 404
        asyncio.run(scenario())
