from sqlalchemy import or_
from typing import Tuple, Optional, List, Dict

from airembr.model.system.context import get_context
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.model.metadata.sys_destination import Destination
from airembr.system.adapter.metadata.mysql.mapping.destination_mapping import map_to_destination_table, map_to_destination
from airembr.system.adapter.metadata.mysql.schema.table import DestinationTable
from airembr.sdk.storage.metadata.query.table_filtering import where_tenant_and_mode_context
from airembr.sdk.storage.metadata.query.select_result import SelectResult


def _merging_data_from_prod_and_sandbox(rows: List[dict], production: bool) -> Dict[str, dict]:
    merged = {}
    production = 1 if production is True else 0
    for row in rows:
        if row.get('production', None) == production:
            merged[row['id']] = row
    return merged

class DestinationService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(DestinationTable, search, limit, offset)

    async def load_by_id(self, destination_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(DestinationTable, primary_id=destination_id)

    async def delete_by_id(self, destination_id: str) -> Tuple[bool, Optional[Destination]]:
        return await self.proxy.delete_by_id_in_deployment_mode(DestinationTable, map_to_destination,
                                                                primary_id=destination_id)

    async def insert(self, destination: Destination):
        return await self.proxy.replace(DestinationTable, map_to_destination_table(destination))

    # Custom

    async def load_enabled_destinations(self, trigger_type: str, event_type: str = None) -> SelectResult:

        if event_type is None:
            where = where_tenant_and_mode_context(
                DestinationTable,
                DestinationTable.enabled == True,
                DestinationTable.trigger_type_id == trigger_type
            )
        else:
            where = where_tenant_and_mode_context(
                DestinationTable,
                DestinationTable.enabled == True,
                DestinationTable.trigger_type_id == trigger_type,
                DestinationTable.event_type_id == event_type
            )

        return await self.proxy.select_in_deployment_mode(DestinationTable, where=where)

    async def load_event_destinations(self, event_type: str, source_id: str) -> SelectResult:
        where = where_tenant_and_mode_context(
            DestinationTable,
            DestinationTable.enabled == True,
            DestinationTable.on_profile_change_only == False,
            DestinationTable.source_id == source_id,
            or_(DestinationTable.event_type_id == event_type, DestinationTable.event_type_id == None,
                DestinationTable.event_type_id == ""),
        )
        return await self.proxy.select_in_deployment_mode(DestinationTable, where=where)

    async def load_destination_resources(self) -> Dict[str, dict]:
        context = get_context()

        if context.production:
            return await self.proxy.query(
                "SELECT * "
                "FROM sys_v_destination_resource "
                "WHERE tenant = :tenant AND production = 1",
                params={"tenant": context.tenant})

        # Sandbox mode (load all regardless of the context)
        result = await self.proxy.query(
            "SELECT * FROM sys_v_destination_resource "
            "WHERE tenant = :tenant",
            params={"tenant": context.tenant})

        # Iterate first production
        rows = result.mappings().all()
        production_rows = _merging_data_from_prod_and_sandbox(rows, production=True)

        # Then sandbox
        sand_box_rows = _merging_data_from_prod_and_sandbox(rows, production=False)

        # Override production with sandbox
        production_rows.update(sand_box_rows)

        # Return merged
        return production_rows