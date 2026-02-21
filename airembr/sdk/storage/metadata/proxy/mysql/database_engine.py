from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from airembr.sdk.storage.metadata.db_context import current_md_database_name
from airembr.sdk.storage.metadata.proxy.mysql.database_config import mysql_config
from airembr.sdk.common.singleton import Singleton

class AsyncMySqlEngine(metaclass=Singleton):

    def __init__(self, echo: bool = None):
        self.default = None
        self.engines = {}
        self.echo = mysql_config.mysql_echo if echo is None else echo

    def _get_sql_engine(self, md_database=None):
        if md_database:
            db_url = f"{mysql_config.mysql_database_uri}/{md_database}"
        else:
            db_url = mysql_config.mysql_database_uri
        return create_async_engine(
            db_url,
            pool_size=mysql_config.pool_size,
            max_overflow=mysql_config.pool_max_overflow,
            pool_timeout=mysql_config.pool_timeout,
            pool_recycle=mysql_config.pool_recycle,
            echo=self.echo)

    def get_session(self):
        return sessionmaker(
            bind=self.get_engine_for_database(),
            class_=AsyncSession,
            expire_on_commit=False
        )

    def get_engine(self):
        if self.default is None:
            self.default = self._get_sql_engine()
        return self.default

    async def close_engines(self):
        for engine in self.engines.values():
            await engine.dispose()

    def get_engine_for_database(self):
        md_database = current_md_database_name()
        if md_database not in self.engines:
            self.engines[md_database] = self._get_sql_engine(md_database)
        return self.engines[md_database]
