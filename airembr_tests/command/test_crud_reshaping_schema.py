import asyncio
from uuid import uuid4

import pytest

from airembr.model.system.context import Context, ServerContext
from airembr.model.system.named_entity import NamedEntity
from airembr.model.metadata.sys_evt_reshaping import EventReshapingSchema, ReshapeSchema, EventReshapeDefinition
from airembr.system.command.v1.errors.reshaping_schema_errors import EventReshapingError
from airembr.system.command.v1.meta.reshaping_schema.reshaping_schema import (
    add_reshape_schema,
    get_reshape_schema,
    delete_reshape_schema,
)


def _make_reshaping_schema(reshaping_id: str) -> EventReshapingSchema:
    return EventReshapingSchema(
        id=reshaping_id,
        name="Test Reshaping Schema",
        event_type="test-event",
        entity_type="person",
        event_source=NamedEntity(id="src-1", name="Source"),
        reshaping=ReshapeSchema(reshape_schema=EventReshapeDefinition()),
    )


def test_crud_reshaping_schema_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            reshaping_id = f"test-reshaping-{uuid4()}"
            await add_reshape_schema(_make_reshaping_schema(reshaping_id))

            fetched = await get_reshape_schema(reshaping_id)

            assert fetched is not None
            assert fetched.id == reshaping_id
            assert fetched.name == "Test Reshaping Schema"
        asyncio.run(scenario())


def test_crud_reshaping_schema_delete():
    with ServerContext(Context()):
        async def scenario():
            reshaping_id = f"test-reshaping-{uuid4()}"
            await add_reshape_schema(_make_reshaping_schema(reshaping_id))

            await delete_reshape_schema(reshaping_id)

            with pytest.raises(EventReshapingError):
                await get_reshape_schema(reshaping_id)
        asyncio.run(scenario())


def test_crud_reshaping_schema_get_missing_raises_404():
    with ServerContext(Context()):
        async def scenario():
            with pytest.raises(EventReshapingError) as exc_info:
                await get_reshape_schema(f"test-reshaping-{uuid4()}")
            assert exc_info.value.status_code == 404
        asyncio.run(scenario())
