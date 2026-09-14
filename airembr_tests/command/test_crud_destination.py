import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.system.named_entity import NamedEntity
from airembr.model.metadata.sys_destination import Destination, DestinationConfig, DestinationResource, DestinationTrigger
from airembr.system.command.v1.meta.destination.destination import save_destination, get_destination, delete_destination_by_id


def _make_destination(destination_id: str) -> Destination:
    return Destination(
        id=destination_id,
        name="Test Destination",
        destination=DestinationConfig(package="some.module.SomeClass"),
        resource=DestinationResource(id="res-1", type="workflow"),
        source=NamedEntity(id="src-1", name="Source"),
        trigger=DestinationTrigger(type=NamedEntity(id="trig-1", name="Trigger")),
    )


def test_crud_destination_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            destination_id = f"test-destination-{uuid4()}"
            await save_destination(_make_destination(destination_id))

            fetched = await get_destination(destination_id)

            assert fetched is not None
            assert fetched.id == destination_id
            assert fetched.name == "Test Destination"
        asyncio.run(scenario())


def test_crud_destination_delete():
    with ServerContext(Context()):
        async def scenario():
            destination_id = f"test-destination-{uuid4()}"
            await save_destination(_make_destination(destination_id))

            result = await delete_destination_by_id(destination_id)

            assert result is True
            assert await get_destination(destination_id) is None
        asyncio.run(scenario())
