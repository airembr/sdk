from collections import namedtuple
from typing import Optional, Type, Callable, Tuple, TypeVar, List

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.sql import text
from sqlalchemy import inspect, update, Column

from airembr.sdk.logging.log_handler import get_logger
from airembr.sdk.storage.metadata.proxy.sqlite.database_engine import AsyncSqliteEngine
from airembr.sdk.model.context import get_context
from airembr.sdk.common.singleton import Singleton
from airembr.sdk.storage.metadata.db_base import Base

# Query utils
from airembr.sdk.storage.metadata.query.table_filtering import where_with_context, where_tenant_and_mode_context
from airembr.sdk.storage.metadata.query.query_service import MysqlQuery, MysqlQueryInDeploymentMode
from airembr.sdk.storage.metadata.query.select_result import SelectResult

T = TypeVar('T')
logger = get_logger(__name__)

SqlContext = namedtuple("SqlContext", ["sql", "params"])

class TableService(metaclass=Singleton):

    def __init__(self):
        self.client = AsyncSqliteEngine()

    @staticmethod
    def get_local_context() -> SqlContext:
        context = get_context()
        return SqlContext(sql=f"tenant = :tenant AND production = :production",
                params={"tenant": context.tenant, "production": context.production})

    @staticmethod
    def get_tenant_context() -> SqlContext:
        context = get_context()
        return SqlContext(sql=f"tenant = :tenant",
                          params={"tenant": context.tenant})

    async def _select_in_deployment_mode(self,
                                         table: Type[Base],
                                         columns=None,
                                         where: Callable = None,
                                         order_by: Column = None,
                                         limit: int = None,
                                         offset: int = None,
                                         distinct: bool = False,
                                         one_record: bool = False
                                         ) -> SelectResult:

        local_session = self.client.get_session()
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query

                resource = MysqlQueryInDeploymentMode(session)
                result = await resource.select(table,
                                               columns,
                                               where,
                                               order_by,
                                               limit,
                                               offset,
                                               distinct)
                # Fetch all results
                if one_record:
                    return SelectResult(result.one_or_none())
                return SelectResult(result.all())

    async def _load_by_id_in_deployment_mode(self,
                                             table: Type[Base],
                                             primary_id: str
                                             ) -> SelectResult:

        where = where_tenant_and_mode_context(table, table.id == primary_id)

        local_session = self.client.get_session()
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                return await self._select_in_deployment_mode(
                    table=table,
                    where=where,
                    one_record=True
                )

    async def _load_by_query_in_deployment_mode(self,
                                                table: Type[Base],
                                                where
                                                ) -> SelectResult:

        where = where_tenant_and_mode_context(table, where)

        local_session = self.client.get_session()
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                return await self._select_in_deployment_mode(
                    table=table,
                    where=where,
                    one_record=True
                )

    async def _delete_by_id_in_deployment_mode(self,
                                               table: Type[Base],
                                               mapper: Callable[[Base], T],
                                               primary_id: str) -> Tuple[bool, Optional[T]]:

        local_session = self.client.get_session()
        async with local_session() as session:
            async with session.begin():
                resource = MysqlQueryInDeploymentMode(session)
                deleted, record = await resource.delete_by_id(table, primary_id)
                return deleted, record.map_to_object(mapper)

    async def _load_all_in_deployment_mode(self, table,
                                           search: Optional[str] = None,
                                           limit: int = None,
                                           offset: int = None,
                                           columns=None,
                                           order_by=None
                                           ) -> SelectResult:
        and_clauses = []
        if search:
            and_clauses.append(table.name.like(f'%{search}%'))

        where = where_tenant_and_mode_context(table, *and_clauses)

        return await self._select_in_deployment_mode(table,
                                                     where=where,
                                                     order_by=order_by,
                                                     columns=columns,
                                                     limit=limit,
                                                     offset=offset)

    async def _load_all_not_in_deployment_mode(self, table,
                                               search: Optional[str] = None,
                                               limit: int = None,
                                               offset: int = None,
                                               columns=None,
                                               order_by=None
                                               ) -> SelectResult:
        and_clauses = []
        if search:
            and_clauses.append(table.name.like(f'%{search}%'))

        where = where_tenant_and_mode_context(table, *and_clauses)

        return await self._select_query(table,
                                        where=where,
                                        order_by=order_by,
                                        columns=columns,
                                        limit=limit,
                                        offset=offset)

    async def exists(self, table_name: str) -> bool:

        local_session = self.client.get_session()

        async with local_session() as session:
            async with session.begin():
                # Use a raw SQL query to check for table existence
                query = text("SELECT name FROM sqlite_master WHERE type = 'table' AND name = :table_name")
                result = await session.execute(query, {"table_name": table_name})
                return result.scalar() is not None

    async def _base_load_all(self,
                             table: Type[Base],
                             columns=None,
                             order_by: Column = None,
                             limit: int = None,
                             offset: int = None,
                             distinct: bool = False,
                             server_context: bool = True) -> SelectResult:

        where = where_with_context(table, server_context)

        return await self._select_query(
            table,
            columns,
            where,
            order_by,
            limit,
            offset,
            distinct
        )

    async def _load_by_id(self, table: Type[Base],
                          primary_id: str,
                          server_context: bool = True
                          ) -> SelectResult:
        local_session = self.client.get_session()

        where = where_with_context(table, server_context, table.id == primary_id)

        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                return await self._select_query(
                    table=table,
                    where=where,
                    one_record=True
                )

    async def _load_by_query_id(self, table: Type[Base],
                                condition,
                                server_context: bool = True
                                ) -> SelectResult:
        local_session = self.client.get_session()

        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                where = where_with_context(table, server_context, condition)
                # Use SQLAlchemy core to perform an asynchronous query
                return await self._select_query(
                    table=table,
                    where=where,
                    one_record=True
                )

    async def _field_filter(self, table: Type[Base], field: Column, value, server_context: bool = True) -> SelectResult:
        local_session = self.client.get_session()

        where = where_with_context(table, server_context, field == value)

        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                return await self._select_query(
                    table=table,
                    where=where,
                    one_record=False
                )

    async def _select_query(self,
                            table: Type[Base],
                            columns=None,
                            where: Callable = None,
                            order_by: Column = None,
                            limit: int = None,
                            offset: int = None,
                            distinct: bool = False,
                            one_record: bool = False
                            ) -> SelectResult:

        local_session = self.client.get_session()
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query

                resource = MysqlQuery(session)
                result = await resource.select(table,
                                               columns,
                                               where,
                                               order_by,
                                               limit,
                                               offset,
                                               distinct)

                # Fetch all results
                if one_record:
                    return SelectResult(result.one_or_none())
                return SelectResult(result.all())

    async def _insert(self, table: Type[Base]) -> Optional[str]:
        local_session = self.client.get_session()
        async with local_session() as session:
            async with session.begin():
                session.add(table)
                return table.id

    async def _insert_many(self, tables: List[Base]) -> List[str]:
        local_session = self.client.get_session()
        async with local_session() as session:
            async with session.begin():
                session.add_all(tables)
            # No need to call commit again — session.begin() handles it
            return [table.id for table in tables]

    # async def _insert_many_stmt(self, table_cls: Type[Base], data: List[Base], upsert=False):
    #     # Convert model instances to dictionaries
    #     data_dicts = [
    #         {
    #             column.key: getattr(item, column.key)
    #             for column in inspect(item).mapper.column_attrs
    #         }
    #         for item in data
    #     ]
    #
    #     stmt = insert(table_cls).values(data_dicts)
    #
    #     if upsert:
    #         update_dict = {
    #             key: stmt.inserted[key] for key in data_dicts[0].keys() if key != 'id'
    #         }
    #
    #         stmt = stmt.on_duplicate_key_update(**update_dict)
    #     return stmt

    async def _update_by_id(self, table: Type[Base], primary_id: str, new_data: dict, server_context: bool = True) -> \
            Optional[str]:
        local_session = self.client.get_session()
        where = where_with_context(table, server_context, table.id == primary_id)

        async with local_session() as session:
            async with session.begin():
                stmt = (
                    update(table)
                    .where(where)
                    .values(**new_data)
                )
                await session.execute(stmt)
                await session.commit()
                return primary_id

    async def _update_by_query_id(self, table: Type[Base], new_data: dict, condition, server_context: bool = True):
        local_session = self.client.get_session()
        where = where_with_context(table, server_context, condition)

        async with local_session() as session:
            async with session.begin():
                stmt = (
                    update(table)
                    .where(where)
                    .values(**new_data)
                )
                await session.execute(stmt)
                await session.commit()

    async def _update_query(self, table: Type[Base], where, new_data: dict):
        local_session = self.client.get_session()
        async with local_session() as session:
            async with session.begin():
                resource = MysqlQuery(session)
                await resource.update(table, new_data, where)
                await session.commit()
                return None

    async def _query(self, sql, params):
        local_session = self.client.get_session()
        async with local_session() as session:
            async with session.begin():
                return await session.execute(text(sql), params)

    def _insert_stmt(self, table: Type[Base], instance: Base, duplicate: bool = True):
        # Convert the SQLAlchemy instance to a dictionary
        data = {c.key: getattr(instance, c.key) for c in inspect(instance).mapper.column_attrs}
        stmt = insert(table).values(**data)
        primary_keys = [key.name for key in inspect(table).primary_key]
        update_dict = {key: value for key, value in data.items() if key not in primary_keys}

        if not duplicate:
            return stmt

        return stmt.on_conflict_do_update(
                index_elements=primary_keys,  # column with UNIQUE constraint
                set_=update_dict
            )

    async def _replace(self, table: Type[Base], instance: Base) -> Optional[str]:
        local_session = self.client.get_session()
        async with local_session() as session:
            async with session.begin():
                upsert_stmt = self._insert_stmt(table, instance)
                await session.execute(upsert_stmt)
                await session.commit()

                # Assuming the primary key field is named 'id'
                return getattr(instance, 'id', None)

    async def _insert_if_none(self, table: Type[Base], data, server_context: bool = True) -> Optional[str]:

        local_session = self.client.get_session()
        where = where_with_context(table, server_context, table.id == data.id)

        async with local_session() as session:
            async with session.begin():
                resource = MysqlQuery(session)
                result = await resource.select(
                    table=table,
                    where=where)

                if result.empty():
                    # Add the new object to the session
                    resource.insert(data)

                    # The actual commit happens here
                    await session.commit()

                    # Return the id of the new record
                    return data.id

                return None

    async def _delete_by_id(self,
                            table: Type[Base],
                            primary_id: str,
                            server_context: bool = True) -> tuple:

        where = where_with_context(table, server_context, table.id == primary_id)

        local_session = self.client.get_session()
        async with local_session() as session:
            async with session.begin():
                resource = MysqlQuery(session)
                await resource.delete(table, where)

        return True, None

    async def _delete_query(self, table: Type[Base], where):

        local_session = self.client.get_session()
        async with local_session() as session:
            async with session.begin():
                resource = MysqlQuery(session)
                await resource.delete(table, where)
