from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from airembr.sdk.storage.metadata.query.table_filtering import where_with_context
from airembr.model.metadata.sys_configuration import Configuration
from airembr.system.adapter.metadata.mysql.mapping.configuration_mapping import map_to_configuration_table
from airembr.system.adapter.metadata.mysql.schema.table import ConfigurationTable


# --------------------------------------------------------
# This Service Runs in Production and None-Production Mode
# It is PRODUCTION CONTEXT-LESS
# --------------------------------------------------------

def _where_with_context(*clause):
    return where_with_context(
        ConfigurationTable,
        False,
        *clause
    )

class ConfigurationService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        if search:
            where = _where_with_context(
                ConfigurationTable.name.like(f'%{search}%')
            )
        else:
            where = _where_with_context()

        return await self.proxy.select_query(ConfigurationTable,
                                        where=where,
                                        order_by=ConfigurationTable.name,
                                        limit=limit,
                                        offset=offset)


    async def load_by_id(self, configuration_id: str) -> SelectResult:
        return await self.proxy.load_by_id(ConfigurationTable, primary_id=configuration_id, server_context=False)

    async def delete_by_id(self, configuration_id: str) -> tuple:
        return await self.proxy.delete_by_id(ConfigurationTable,
                                        primary_id=configuration_id,
                                        server_context=False)

    async def upsert(self, configuration: Configuration):
        return await self.proxy.replace(ConfigurationTable, map_to_configuration_table(configuration))


    