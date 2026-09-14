import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.system.named_entity import NamedEntity
from airembr.model.metadata.sys_source import EventSource
from airembr.system.command.v1.meta.source.event_source import (
    save_event_source,
    load_source_by_id,
    delete_event_source,
)


def _make_event_source(source_id: str) -> EventSource:
    return EventSource(
        id=source_id,
        name="Test Source",
        type=["webhook"],
        bridge=NamedEntity(id="bridge-1", name="Bridge"),
    )


def test_crud_source_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            source_id = f"test-source-{uuid4()}"
            await save_event_source(_make_event_source(source_id))

            fetched = await load_source_by_id(source_id)

            assert fetched is not None
            assert fetched.id == source_id
            assert fetched.name == "Test Source"
        asyncio.run(scenario())


def test_crud_source_delete():
    with ServerContext(Context()):
        async def scenario():
            source_id = f"test-source-{uuid4()}"
            await save_event_source(_make_event_source(source_id))

            await delete_event_source(source_id)

            assert await load_source_by_id(source_id) is None
        asyncio.run(scenario())
