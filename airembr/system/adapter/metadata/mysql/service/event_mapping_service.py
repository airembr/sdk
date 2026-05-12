from typing import Tuple, Optional, List

from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy

from airembr.model.metadata.sys_event_mapping import EventTypeMetadata
from airembr.system.adapter.metadata.mysql.mapping.event_to_event_mapping import map_to_event_mapping_table, \
    map_to_event_mapping
from airembr.system.adapter.metadata.mysql.schema.table import EventMappingTable
from airembr.sdk.storage.metadata.query.table_filtering import where_tenant_and_mode_context
from airembr.sdk.storage.metadata.query.select_result import SelectResult


class EventMappingService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(EventMappingTable, search, limit, offset)

    async def load_by_id(self, event_mapping_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(EventMappingTable, primary_id=event_mapping_id)

    async def delete_by_id(self, event_mapping_id: str) -> Tuple[bool, Optional[EventTypeMetadata]]:
        return await self.proxy.delete_by_id_in_deployment_mode(EventMappingTable, map_to_event_mapping,
                                                           primary_id=event_mapping_id)

    async def insert(self, event_type_metadata: EventTypeMetadata):
        return await self.proxy.replace(EventMappingTable, map_to_event_mapping_table(event_type_metadata))

    async def load_by_event_type(self, event_type: str, only_enabled: bool = True) -> SelectResult:
        if only_enabled:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type == event_type,
                EventMappingTable.enabled == only_enabled
            )
        else:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type == event_type
            )

        return await self.proxy.select_in_deployment_mode(EventMappingTable,
                                                     where=where,
                                                     order_by=EventMappingTable.name
                                                     )

    async def load_by_event_types(self, event_types: List[str], only_enabled: bool = True) -> SelectResult:
        if only_enabled:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type.in_(event_types),
                EventMappingTable.enabled == only_enabled
            )
        else:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type.in_(event_types)
            )

        return await self.proxy.select_in_deployment_mode(EventMappingTable,
                                                     where=where,
                                                     order_by=EventMappingTable.name
                                                     )

    async def load_by_event_type_id(self, event_type_id: str, only_enabled: bool = True) -> SelectResult:
        if only_enabled:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type == event_type_id,
                EventMappingTable.enabled == only_enabled
            )
        else:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type == event_type_id
            )
        return await self.proxy.select_in_deployment_mode(EventMappingTable,
                                                     where=where,
                                                     order_by=EventMappingTable.name,
                                                     one_record=True
                                                     )
