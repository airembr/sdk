import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_bridge import Bridge
from airembr.system.adapter.metadata.mysql.service.bridge_service import BridgeService
from airembr.system.command.v1.meta.bridge.bridge import get_data_bridge_by_id


def test_get_data_bridge_by_id_found():
    with ServerContext(Context()):
        async def scenario():
            bridge_id = f"test-bridge-{uuid4()}"
            bridge = Bridge(id=bridge_id, name="Test Bridge", type="webhook")
            await BridgeService().insert(bridge)

            fetched = await get_data_bridge_by_id(bridge_id)

            assert fetched is not None
            assert fetched.id == bridge_id
            assert fetched.name == "Test Bridge"
            assert fetched.type == "webhook"
        asyncio.run(scenario())


def test_get_data_bridge_by_id_not_found():
    with ServerContext(Context()):
        async def scenario():
            fetched = await get_data_bridge_by_id(f"test-bridge-{uuid4()}")
            assert fetched is None
        asyncio.run(scenario())
