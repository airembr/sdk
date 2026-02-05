from collections import OrderedDict
from typing import Type, Callable, Optional, TypeVar, Tuple, Any

from sqlalchemy import Column, update, delete, ChunkedIteratorResult, select, Select

from airembr.sdk.storage.metadata.query.context_filter import context_filter
from airembr.sdk.model.context import get_context, ServerContext
from airembr.sdk.storage.metadata.db_base import Base
from airembr.sdk.storage.metadata.query.select_result import SelectResult

T = TypeVar('T')


class MySqlQueryResult:
    """
    Standardizes the output form MysqlQuery
    """

    def __init__(self, data):
        self.data = data

    def all(self):
        if isinstance(self.data, ChunkedIteratorResult):
            return self.data.scalars().all()
        else:
            return self.data

    def one_or_none(self):
        if isinstance(self.data, ChunkedIteratorResult):
            return self.data.scalars().one_or_none()
        else:
            return self.data[0] if self.data else None

    def one(self):
        if isinstance(self.data, ChunkedIteratorResult):
            return self.data.scalars().one()
        else:
            return self.data[0]

    def empty(self) -> bool:
        if isinstance(self.data, ChunkedIteratorResult):
            return self.data.first() is None
        else:
            return not bool(self.data)


class BaseMysqlQuery:

    def __init__(self, session):
        self.session = session

    @staticmethod
    def _select_clause(table: Type[Base],
                       columns=None,
                       where: Optional[Callable] = None,
                       order_by: Column = None,
                       limit: int = None,
                       offset: int = None,
                       distinct: bool = False) -> Select[Any]:

        if columns is not None:
            _select = select(*columns)
        else:
            _select = select(table)

        if distinct:
            _select = _select.distinct()

        if where is not None:
            _select = _select.where(where())

        if order_by is not None:
            _select = _select.order_by(order_by)

        if limit:
            _select = _select.limit(limit)

            if offset:
                _select = _select.offset(offset)

        return _select


class MysqlQueryInDeploymentMode(BaseMysqlQuery):

    async def _load_by_id(self, table: Type[Base], primary_id: str, production: bool) -> SelectResult:
        context = get_context()

        where = context_filter(table, context.tenant, production, table.id == primary_id)

        query = self._select_clause(table, where=where)

        result = await self.session.execute(query)

        return SelectResult(result.scalar())

    async def delete_by_query(self, table: Type[Base], query):
        context = get_context()

        where = context_filter(table, context.tenant, context.production, query)
        stmt = delete(table).where(where())
        await self.session.execute(stmt)

    async def delete_by_id(self, table: Type[Base], primary_id) -> Tuple[bool, SelectResult]:
        context = get_context()

        where = context_filter(table, context.tenant, context.production, table.id == primary_id)
        await self.session.execute(
            delete(table).where(where())
        )

        if context.is_production():
            # If in production then test context does not matter, return SelectResult(None)
            return True, SelectResult(None)

        # Loads regardless of context (production, or test)
        record = await self._load_by_id(
            table,
            primary_id=primary_id,
            production=not context.production
        )
        return True, record

    @staticmethod
    async def load_query(session, query_lambda) -> MySqlQueryResult:

        context = get_context()

        # This is loadig in production mode.

        if context.is_production():
            production_data = await session.execute(query_lambda())
            production_list = []
            for item in production_data.scalars().all():
                item.running = True
                production_list.append(item)
            return MySqlQueryResult(production_list)

        # This is loadig in test mode

        with ServerContext(context.switch_context(production=False)):
            test_data = await session.execute(query_lambda())

            with ServerContext(context.switch_context(production=True)):
                production_data = await session.execute(query_lambda())

                # Assuming result1 and result2 are the results of your two queries

                # Convert results to dictionaries

                production_dict = OrderedDict()
                for item in production_data.scalars().all():
                    item.running = True
                    production_dict[item.id] = item

                test_dict = OrderedDict()
                for item in test_data.scalars().all():
                    if item.id in production_dict:
                        item.running = True
                    test_dict[item.id] = item

                # Merge the dictionaries
                # Entries in dict_result2 will override those in dict_result1 for matching keys

                production_dict.update(test_dict)

                # Convert the merged dictionary back to a list of model instances

                merged_results = list(production_dict.values())

                return MySqlQueryResult(merged_results)


    async def select(self,
                     table: Type[Base],
                     columns=None,
                     where: Optional[Callable] = None,
                     order_by: Column = None,
                     limit: int = None,
                     offset: int = None,
                     distinct: bool = False) -> MySqlQueryResult:

        def query_lambda():
            return self._select_clause(table,
                                       columns,
                                       where,
                                       order_by,
                                       limit,
                                       offset,
                                       distinct)

        return await self.load_query(self.session, query_lambda)


class MysqlQuery(BaseMysqlQuery):

    async def update(self, table: Type[Base], new_data, where: Optional[Callable] = None):
        stmt = (
            update(table)
            .where(where())
            .values(**new_data)
        )
        return await self.session.execute(stmt)

    async def delete(self, table: Type[Base], where: Optional[Callable] = None):
        return await self.session.execute(
            delete(table).where(where())
        )

    async def select(self,
                     table: Type[Base],
                     columns=None,
                     where: Optional[Callable] = None,
                     order_by: Column = None,
                     limit: int = None,
                     offset: int = None,
                     distinct: bool = False) -> MySqlQueryResult:
        query = self._select_clause(table,
                                    columns,
                                    where,
                                    order_by,
                                    limit,
                                    offset,
                                    distinct)

        return MySqlQueryResult(await self.session.execute(query))

    def insert(self, data):
        return self.session.add(data)
