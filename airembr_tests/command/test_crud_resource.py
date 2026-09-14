import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_resource import Resource
from airembr.system.command.v1.meta.resource.resource import upsert_resource, get_resource_by_id, delete_resource


def test_crud_resource_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            resource_id = f"test-resource-{uuid4()}"
            await upsert_resource(Resource(id=resource_id, name="Test Resource", type="database"))

            fetched = await get_resource_by_id(resource_id)

            assert fetched is not None
            assert fetched.id == resource_id
            assert fetched.name == "Test Resource"
        asyncio.run(scenario())


def test_crud_resource_upsert_updates_existing():
    with ServerContext(Context()):
        async def scenario():
            resource_id = f"test-resource-{uuid4()}"
            await upsert_resource(Resource(id=resource_id, name="Test Resource", type="database"))
            await upsert_resource(Resource(id=resource_id, name="Updated Resource", type="database"))

            fetched = await get_resource_by_id(resource_id)

            assert fetched is not None
            assert fetched.name == "Updated Resource"
        asyncio.run(scenario())


def test_crud_resource_delete():
    with ServerContext(Context()):
        async def scenario():
            resource_id = f"test-resource-{uuid4()}"
            await upsert_resource(Resource(id=resource_id, name="Test Resource", type="database"))

            await delete_resource(resource_id)

            assert await get_resource_by_id(resource_id) is None
        asyncio.run(scenario())
