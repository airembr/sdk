from airembr.sdk.storage.metadata.db_config import meta_data_adapter
from airembr.sdk.storage.metadata.proxy.sqlite.table_service import TableService as SqliteTableService
from airembr.sdk.storage.metadata.proxy.mysql.table_service import TableService as MysqlTableService


class TableServiceProxy:

    def __init__(self):
        if meta_data_adapter == 'mysql':
            self.ts = MysqlTableService()
        else:
            self.ts = SqliteTableService()

    async def select_in_deployment_mode(self, *args, **kwargs):
        return await self.ts._select_in_deployment_mode(*args, **kwargs)

    async def load_by_id_in_deployment_mode(self, *args, **kwargs):
        return await self.ts._load_by_id_in_deployment_mode(*args, **kwargs)

    async def load_by_query_in_deployment_mode(self, *args, **kwargs):
        return await self.ts._load_by_query_in_deployment_mode(*args, **kwargs)

    async def delete_by_id_in_deployment_mode(self, *args, **kwargs):
        return await self.ts._delete_by_id_in_deployment_mode(*args, **kwargs)

    async def load_all_in_deployment_mode(self, *args, **kwargs):
        return await self.ts._load_all_in_deployment_mode(*args, **kwargs)

    async def exists(self, *args, **kwargs):
        return await self.ts.exists(*args, **kwargs)

    # No deployment mode
    async def base_load_all(self, *args, **kwargs):
        return await self.ts._base_load_all(*args, **kwargs)

    # No deployment mode
    async def load_all_not_in_deployment_mode(self, *args, **kwargs):
        return await self.ts._load_all_not_in_deployment_mode(*args, **kwargs)

    async def load_by_id(self, *args, **kwargs):
        return await self.ts._load_by_id(*args, **kwargs)

    async def load_by_query_id(self, *args, **kwargs):
        return await self.ts._load_by_query_id(*args, **kwargs)

    async def field_filter(self, *args, **kwargs):
        return await self.ts._field_filter(*args, **kwargs)

    async def select_query(self, *args, **kwargs):
        return await self.ts._select_query(*args, **kwargs)

    async def insert(self, *args, **kwargs):
        return await self.ts._insert(*args, **kwargs)

    async def insert_many(self, *args, **kwargs):
        return await self.ts._insert_many(*args, **kwargs)

    # async def insert_many_stmt(self, *args, **kwargs):
    #     return await self.ts._insert_many_stmt(*args, **kwargs)

    async def update_by_id(self, *args, **kwargs):
        return await self.ts._update_by_id(*args, **kwargs)

    async def update_by_query_id(self, *args, **kwargs):
        return await self.ts._update_by_query_id(*args, **kwargs)

    async def update_query(self, *args, **kwargs):
        return await self.ts._update_query(*args, **kwargs)

    async def query(self, *args, **kwargs):
        return await self.ts._query(*args, **kwargs)

    def insert_stmt(self, *args, **kwargs):
        return self.ts._insert_stmt(*args, **kwargs)

    async def replace(self, *args, **kwargs):
        return await self.ts._replace(*args, **kwargs)

    async def insert_if_none(self, *args, **kwargs):
        return await self.ts._insert_if_none(*args, **kwargs)

    async def delete_by_id(self, *args, **kwargs):
        return await self.ts._delete_by_id(*args, **kwargs)

    async def delete_query(self, *args, **kwargs):
        return await self.ts._delete_query(*args, **kwargs)
