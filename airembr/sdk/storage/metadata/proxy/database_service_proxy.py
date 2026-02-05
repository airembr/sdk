import os

from airembr.sdk.storage.metadata.db_config import meta_data_adapter
from airembr.sdk.storage.metadata.proxy.mysql.database_engine import AsyncMySqlEngine
from airembr.sdk.storage.metadata.proxy.mysql.database_service import DatabaseService as MysqlDatabaseService
from airembr.sdk.storage.metadata.proxy.sqlite.database_engine import AsyncSqliteEngine
from airembr.sdk.storage.metadata.proxy.sqlite.database_service import DatabaseService as SqliteDatabaseService


class DatabaseServiceProxy:

    def __init__(self):
        if meta_data_adapter == 'sqlite':
            self.ds = SqliteDatabaseService(AsyncSqliteEngine())
        else:
            self.ds = MysqlDatabaseService(AsyncMySqlEngine())

    def get_current_md_database_name(self):
        return self.ds.get_current_database_name()

    async def create_tables(self, *args, **kwargs):
        return await self.ds._create_tables(*args, **kwargs)

    async def create_database(self, *args, **kwargs):
        return await self.ds._create_database(*args, **kwargs)

    def read_views(self, *args, **kwargs):
        return self.ds._read_views(*args, **kwargs)

    async def create_views(self, *args, **kwargs):
        return await self.ds._create_views(*args, **kwargs)

    async def exists(self, *args, **kwargs):
        return await self.ds.exists(*args, **kwargs)

    async def bootstrap(self, *args, **kwargs):
        return await self.ds.bootstrap(*args, **kwargs)

    async def drop(self, *args, **kwargs):
        return await self.ds.drop(*args, **kwargs)

    async def inspect(self, *args, **kwargs):
        if isinstance(self.ds, SqliteDatabaseService):
            if not os.path.exists(self.ds.client.get_db_file()):
                await self.ds.bootstrap()

        return await self.ds.inspect(*args, **kwargs)
