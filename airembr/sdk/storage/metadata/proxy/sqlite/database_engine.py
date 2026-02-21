from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from airembr.sdk.storage.metadata.db_context import current_md_database_name
from airembr.sdk.storage.metadata.proxy.sqlite.database_config import sqlite_config
from airembr.sdk.common.singleton import Singleton


class AsyncSqliteEngine(metaclass=Singleton):

    def __init__(self, echo: bool = None):
        self.default = None
        self.engines = {}

    def get_db_file(self):
        return f"{sqlite_config.sqlite_schema}{sqlite_config.sqlite_host}"

    def _get_sql_engine(self, md_database=None):
        db_url = self.get_db_file()
        return create_async_engine(
            db_url,
            echo=False)

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

    def get_engine_for_database(self):
        md_database = current_md_database_name()
        if md_database not in self.engines:
            self.engines[md_database] = self._get_sql_engine(md_database)
        return self.engines[md_database]
