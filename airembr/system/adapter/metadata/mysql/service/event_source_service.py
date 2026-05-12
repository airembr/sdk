from typing import Tuple, Optional

from sqlalchemy import desc

from airembr.model.metadata.sys_source import EventSource
from airembr.system.adapter.metadata.mysql.mapping.event_source_mapping import map_to_event_source_table, map_to_event_source
from airembr.system.adapter.metadata.mysql.schema.table import EventSourceTable
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.table_filtering import where_tenant_and_mode_context
from airembr.sdk.storage.metadata.query.select_result import SelectResult


class EventSourceService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all_in_deployment_mode(self, search: str = None, limit: int = None,
                                          offset: int = None, order_by=None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(EventSourceTable, search, limit, offset, order_by=order_by)

    async def load_by_id_in_deployment_mode(self, source_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(
            EventSourceTable,
            primary_id=source_id
        )

    async def delete_by_id_in_deployment_mode(self, source_id: str) -> Tuple[
        bool, Optional[EventSource]]:
        return await self.proxy.delete_by_id_in_deployment_mode(
            EventSourceTable,
            map_to_event_source,
            primary_id=source_id
        )

    async def load_by_type_in_deployment_mode(self, type: str) -> SelectResult:
        where = where_tenant_and_mode_context(EventSourceTable, EventSourceTable.type == type)
        return await self.proxy.select_in_deployment_mode(
            EventSourceTable,
            where=where
        )

    async def load_active_by_bridge_id(self, bridge_id: str) -> SelectResult:
        # It is PRODUCTION CONTEXT-LESS
        return await self.proxy.select_in_deployment_mode(
            EventSourceTable,
            where=where_tenant_and_mode_context(
                EventSourceTable,
                EventSourceTable.bridge_id == bridge_id,
                EventSourceTable.enabled == True
            )
        )

    async def load_active_by_bridge_type(self, bridge_type: str) -> SelectResult:
        # It is PRODUCTION CONTEXT-LESS
        return await self.proxy.select_query(
            EventSourceTable,
            where=where_tenant_and_mode_context(
                EventSourceTable,
                EventSourceTable.type == bridge_type,
                EventSourceTable.enabled == True
            )
        )

    async def load_active(self, limit) -> SelectResult:
        # It is PRODUCTION CONTEXT-LESS
        return await self.proxy.select_in_deployment_mode(
            EventSourceTable,
            where=where_tenant_and_mode_context(
                EventSourceTable,
                EventSourceTable.enabled == True
            ),
            limit=limit,
            order_by=desc(EventSourceTable.timestamp)
        )

    async def insert(self, event_source: EventSource):
        return await self.proxy.replace(EventSourceTable, map_to_event_source_table(event_source))

    async def lock_by_bridge_id(self, bridge_id: str, lock):
        # It is PRODUCTION CONTEXT-LESS
        return await self.proxy.update_query(
            EventSourceTable,
            where=(
                where_tenant_and_mode_context(
                    EventSourceTable,
                    EventSourceTable.bridge_id == bridge_id
                )
            ),
            new_data={
                'locked': lock
            }
        )

    @staticmethod
    def event_source_types():
        standard_inbound_sources = {
            "rest": {
                "name": "Rest Api Call",
                "tags": ["rest", "inbound"]
            },
            "redirect": {
                "name": "Redirect Link",
                "tags": ["link", "inbound"]
            },
            "webhook": {
                "name": "Webhook",
                "tags": ["webhook", "inbound"]
            },
            "imap": {
                "name": "IMAP Server",
                "tags": ["imap", "inbound"]
            },
            "ical": {
                "name": "ICAL File",
                "tags": ['calendar']
            },
            "chat": {
                "name": "Chat",
                "tags": ['chat']
            }
        }

        return standard_inbound_sources

    async def save(self, event_source: EventSource):
        types = self.event_source_types()
        if event_source.is_allowed(types):
            return await self.proxy.replace(EventSourceTable, map_to_event_source_table(event_source))
        else:
            raise ValueError(f"Unknown event source types {event_source.type}. Available {types}.")
