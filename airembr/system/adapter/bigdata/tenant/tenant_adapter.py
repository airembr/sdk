from typing import AsyncGenerator

from airembr.model.system.context import Context
from srd.domain.column import Column
from srd.domain.select import Select
from srd.driver import StarrocksDriver

sr_client = StarrocksDriver()


async def load_bd_databases():
    table_name_col = Column(name="schema_name")
    where = f"{~table_name_col} RLIKE '^bd_'"
    sql = Select('schemata').columns([table_name_col]).where(where)
    sql.database('information_schema')
    return await sr_client.query(~sql)


async def _load_tenant_databases() -> AsyncGenerator[str, None]:
    # Load databases to check
    for database in await load_bd_databases():
        yield database.get("schema_name")


async def load_tenant_database_and_context():
    async for database in _load_tenant_databases():
        # Get tenant
        _, tenant, _, mode = database.split('_')

        yield database, Context(tenant=tenant, production=mode == 'prod')
