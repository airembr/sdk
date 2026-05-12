from typing import Optional, Tuple, List

from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.table_filtering import where_tenant_and_mode_context
from airembr.sdk.storage.metadata.query.select_result import SelectResult

from airembr.model.metadata.sys_evt_validation import EventValidator
from airembr.system.adapter.metadata.mysql.mapping.event_validation_mapping import map_to_event_validation_table, \
    map_to_event_validation
from airembr.system.adapter.metadata.mysql.schema.table import EventValidationTable


class EventValidationService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(EventValidationTable, search, limit, offset)

    async def load_by_id(self, event_validation_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(EventValidationTable, primary_id=event_validation_id)

    async def delete_by_id(self, event_validation_id: str) -> Tuple[bool, Optional[EventValidator]]:
        return await self.proxy.delete_by_id_in_deployment_mode(EventValidationTable, map_to_event_validation,
                                                           primary_id=event_validation_id)

    async def insert(self, event_validation: EventValidator):
        return await self.proxy.replace(EventValidationTable, map_to_event_validation_table(event_validation))

    async def load_by_event_type(self, event_type: str, only_enabled: bool = True):
        if only_enabled:
            where = where_tenant_and_mode_context(
                EventValidationTable,
                EventValidationTable.event_type == event_type,
                EventValidationTable.enabled == only_enabled
            )
        else:
            where = where_tenant_and_mode_context(
                EventValidationTable,
                EventValidationTable.event_type == event_type
            )

        return await self.proxy.select_in_deployment_mode(
            EventValidationTable,
            where=where,
            order_by=EventValidationTable.name)

    async def load_ttls(self, event_types: List[str] = None):
        if event_types:
            where = where_tenant_and_mode_context(
                EventValidationTable,
                EventValidationTable.enabled == True,
                EventValidationTable.ttl>0,
                EventValidationTable.event_type.in_(event_types)  # IN
            )
        else:
            where = where_tenant_and_mode_context(
                EventValidationTable,
                EventValidationTable.ttl > 0,
                EventValidationTable.enabled == True
            )

        return await self.proxy.select_in_deployment_mode(
            EventValidationTable,
            where=where,
            order_by=EventValidationTable.name)
