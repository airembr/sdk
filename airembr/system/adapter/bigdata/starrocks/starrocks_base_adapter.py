import json
from typing import Optional, Union

from airembr.core.singleton import Singleton
# from srd.domain.column import Count
from srd.domain.record_mapping import EntityToTableMapping
from srd.domain.result import Result
# from srd.domain.select import Select
from srd.domain.sql import Sql
from srd.domain.statement import Statement
from srd.domain.table_statement import TableStatement
from srd.driver import StarrocksDriver
# from durable_dot_dict.dotdict import DotDict

from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name


class StarrocksBaseAdapter(metaclass=Singleton):

    def __init__(self):
        self._client = StarrocksDriver()

    @property
    def client(self):
        return self._client

    async def _count(self, table: str, where: Optional[str] = None, params=None) -> Result:
        database = current_bd_database_name()

        sql = (
                Sql(f"SELECT * as `count` FROM {database}.{table}")
              + (bool(where), where, params)
        )

        return await self._client.exec(sql)

    async def stream(self, rows: list, mapping: EntityToTableMapping, timeout: Optional[int] = 10):
        if rows:

            mapping.database = current_bd_database_name()
            result = await self._client.stream(
                current_bd_database_name(),
                mapping.table,
                rows,
                timeout
            )
            text = await result.text()
            response = json.loads(text)

            if response.get("Status", None) == "Fail":
                print(mapping.table, response)
                return "Fail", 0, 0, response.get("Message", None)

            return (
                response.get("Status", None),
                response.get('NumberTotalRows', None),
                response.get('NumberLoadedRows', None),
                response.get('Message', None)
            )
        return None, None, None, None

    async def query(self, sql: Union[Statement, TableStatement], params=None) -> Result:
        # Set tenant context
        if isinstance(sql, TableStatement):
            sql.database(current_bd_database_name())

        return await self._client.query(~sql, params)

    async def exec(self, sql: Sql):
        return await self._client.exec(sql)
