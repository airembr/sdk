from typing import Optional, Tuple

from airembr.model.metadata.sys_resource import Resource
from airembr.system.adapter.metadata.mysql.mapping.resource_mapping import map_to_resource_table, map_to_resource
from airembr.system.adapter.metadata.mysql.schema.table import ResourceTable
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from airembr.sdk.storage.metadata.query.table_filtering import where_tenant_and_mode_context, sql_functions


class ResourceService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(ResourceTable, search, limit, offset)

    async def load_by_id(self, resource_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(ResourceTable, primary_id=resource_id)

    async def delete_by_id(self, resource_id: str) -> Tuple[bool, Optional[Resource]]:
        return await self.proxy.delete_by_id_in_deployment_mode(ResourceTable, map_to_resource,
                                                                primary_id=resource_id)

    async def insert(self, resource: Resource):
        return await self.proxy.replace(ResourceTable, map_to_resource_table(resource))

    async def load_enabled_by_tag(self, tag: str):
        where = where_tenant_and_mode_context(
            ResourceTable,
            sql_functions().find_in_set(tag, ResourceTable.tags) > 0,
            ResourceTable.enabled == True
        )

        return await self.proxy.select_in_deployment_mode(
            ResourceTable,
            where=where
        )
