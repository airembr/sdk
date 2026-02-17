import os
from typing import List, Iterator

from airembr.sdk.storage.metadata.db_config import meta_data_adapter
from airembr.sdk.storage.metadata.proxy.mysql.database_engine import AsyncMySqlEngine
from airembr.sdk.storage.metadata.proxy.mysql.database_service import DatabaseService as MysqlDatabaseService
from airembr.sdk.storage.metadata.proxy.sqlite.database_engine import AsyncSqliteEngine
from airembr.sdk.storage.metadata.proxy.sqlite.database_service import DatabaseService as SqliteDatabaseService


def read_sql_files(sqls: List[str], folder: str) -> Iterator[str]:
    """
    Yields the content of SQL files located in the given folder.

    :param sqls: List of SQL filenames (e.g. ["query1.sql", "query2.sql"])
    :param folder: Path to the folder containing the SQL files
    :return: Generator yielding file contents as strings
    """
    for sql_file in sqls:
        path = os.path.join(folder, sql_file)

        if not os.path.isfile(path):
            raise FileNotFoundError(f"SQL file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            yield f.read()


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

    async def create_view(self, sql: str):
        return await self.ds._create_view(sql)

    async def create_views(self, sqls: List[str], folder: str):
        for sql in read_sql_files(sqls, folder):
            await self.create_view(sql)

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
