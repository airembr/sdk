from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name


class BdMetadataAdapter(AdapterRouter):

    async def list_tables(self):
        sql = (
                Sql()
                + "SELECT  TABLE_NAME, TABLE_TYPE, ENGINE"
                + "FROM INFORMATION_SCHEMA.TABLES"
                + "WHERE TABLE_SCHEMA = :database"
                + "ORDER BY TABLE_NAME"
                + Param({"database": current_bd_database_name()})
        )

        result = await self.adapter.exec(sql)
        return result

    async def list_table_columns(self, table_name: str):
        sql = (
                Sql()
                + "SELECT COLUMN_NAME, DATA_TYPE"
                + "FROM INFORMATION_SCHEMA.COLUMNS"
                + "WHERE TABLE_SCHEMA = :database AND TABLE_NAME = :table_name"
                + "ORDER BY ORDINAL_POSITION"
                + Param({"database": current_bd_database_name(), "table_name": table_name})
        )

        result = await self.adapter.exec(sql)
        return result

    async def list_table_column_names(self, table_name: str):
        records = await self.list_table_columns(table_name)
        return [
            {
                "id": f"{row['COLUMN_NAME']}|{row['DATA_TYPE']}",
                "name": f"{row['COLUMN_NAME']} | {row['DATA_TYPE']}"
            }
            for row in records.list()
        ]

    async def list_table_names(self):
        records = await self.list_tables()
        result = [
            {
                "id": row['TABLE_NAME'],
                "name": row['TABLE_NAME']
            }
            for row in records.list() if not row['TABLE_NAME'].startswith('sys_')
        ]

        return {
            "total": len(result),
            "result": result
        }

    async def list_table_stats(self):
        sql = (
                Sql()
                + "SELECT TABLE_NAME, TABLE_ROWS"
                + "FROM INFORMATION_SCHEMA.TABLES"
                + "WHERE TABLE_SCHEMA = :database"
                + "ORDER BY TABLE_NAME"
                + Param({"database": current_bd_database_name()})
        )

        result = await self.adapter.exec(sql)
        stats = [
            {"table": row["TABLE_NAME"], "rows": row["TABLE_ROWS"]}
            for row in result.list()
        ]
        return {"total": len(stats), "result": stats}
