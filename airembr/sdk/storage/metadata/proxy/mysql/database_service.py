import os

from sqlalchemy import text, inspect

import tracardi.config
from airembr.sdk.storage.metadata.db_context import current_md_database_name
from airembr.sdk.storage.metadata.db_base import Base

_local_dir = os.path.dirname(__file__)


class DatabaseService:
    sql = [
        # None yet
    ]

    def __init__(self, client):
        self.client = client

    async def close(self):
        await self.client.close_engines()

    async def _create_tables(self):
        engine = self.client.get_engine_for_database()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()
        await engine.dispose()

    async def _create_database(self):
        os.makedirs(os.path.dirname(tracardi.config.sqlite.sqlite_host), exist_ok=True)
        engine = self.client.get_engine()
        async with engine.connect() as conn:
            md_database = current_md_database_name()
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{md_database}`"))
            await conn.commit()
        await engine.dispose()

    def _read_views(self):
        for sql in self.sql:
            file = os.path.join(_local_dir, f"../schema/view/{sql}.sql")
            with open(file, "r") as fp:  # Save the JSON into schema.json or adjust the path
                yield fp.read()

    async def _create_views(self):
        engine = self.client.get_engine()
        async with engine.connect() as conn:
            md_database = current_md_database_name()
            for sql in self._read_views():
                sql = sql.replace('{|database|}', md_database)
                await conn.execute(text(sql))
                await conn.commit()
        await engine.dispose()

    async def exists(self, database_name: str) -> bool:
        engine = self.client.get_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text(f"SHOW DATABASES LIKE '{database_name}';"))
            return result.fetchone() is not None

    async def bootstrap(self):

        # Connect to the database
        await self._create_database()

        # Create a new async engine instance with the database selected
        await self._create_tables()

        # Create views
        await self._create_views()

    async def drop(self, database_name):
        engine = self.client.get_engine()
        async with engine.connect() as conn:
            await conn.execute(text(f"DROP DATABASE IF EXISTS `{database_name}`;"))
            await conn.commit()

    async def inspect(self, database_name):
        engine = self.client.get_engine()
        async with engine.begin() as conn:
            def do_check(sync_conn):
                inspector = inspect(sync_conn)

                # Use the database name as schema
                existing_tables = set(inspector.get_table_names(schema=database_name))
                declared_tables = set(Base.metadata.tables.keys())
                missing = declared_tables - existing_tables

                if missing:
                    return missing
                return None
            return await conn.run_sync(do_check)

    @staticmethod
    def get_current_database_name():
        return current_md_database_name()