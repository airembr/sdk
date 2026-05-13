from typing import List

from airembr.model.system.context import get_context
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.model.metadata.sys_bridge import Bridge
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.adapter.metadata.mysql.mapping.bridge_mapping import map_to_bridge_table
from airembr.system.adapter.metadata.mysql.schema.table import BridgeTable
from airembr.sdk.storage.metadata.query.select_result import SelectResult

logger = get_logger(__name__)


class BridgeService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self) -> SelectResult:
        return await self.proxy.base_load_all(BridgeTable, server_context=False)

    async def load_by_id(self, bridge_id: str) -> SelectResult:
        return await self.proxy.load_by_id(BridgeTable, primary_id=bridge_id, server_context=False)

    async def delete_by_id(self, bridge_id: str) -> tuple:
        return await self.proxy.delete_by_id(BridgeTable, primary_id=bridge_id, server_context=False)

    async def insert(self, bridge: Bridge):
        return await self.proxy.insert_if_none(BridgeTable, map_to_bridge_table(bridge), server_context=False)

    async def replace(self, bridge: Bridge):
        return await self.proxy.replace(BridgeTable, map_to_bridge_table(bridge))

    # Custom

    @staticmethod
    async def bootstrap(default_bridges: List[Bridge]):
        context = get_context()
        bs = BridgeService()
        for bridge in default_bridges:
            bridge.id = bridge.get_id_in_context_of_tenant(context)
            await bs.insert(bridge)
            logger.info(f"Bridge {bridge.name} installed with id {bridge.id}.")

    @staticmethod
    async def reinstall(default_bridges: List[Bridge]):
        context = get_context()
        bs = BridgeService()
        for bridge in default_bridges:
            bridge.id = bridge.get_id_in_context_of_tenant(context)
            await bs.replace(bridge)
            logger.info(f"Bridge {bridge.name} reinstalled with id {bridge.id}.")
