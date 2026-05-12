from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.logging.log_handler import get_logger

logger = get_logger(__name__)


class BdSearchAdapter(AdapterRouter):

    # Fields Autocomplete

    async def get_column_values(self, table_mapping, column, limit):
        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT DISTINCT {table_mapping | column} as field"
                + f"FROM {database}.{table_mapping}"
                + "ORDER by field ASC"
                + f"LIMIT :limit" + Param({"limit": limit})
        )

        result = await self.adapter.exec(sql)

        return {row['field'] for row in result if row['field'] is not None}

    async def get_json_field_values(self, table_mapping, entity_type, column, limit):
        database = current_bd_database_name()
        field = f"get_json_string(traits, '$.{column}')"
        sql = (
                Sql(f"SELECT DISTINCT {field} AS field ")
                + f"FROM {database}.{table_mapping}"
                + f"WHERE entity_type = :entity_type AND {field} IS NOT NULL" + Param({"entity_type": entity_type})
                + f"LIMIT :limit" + Param({"limit": limit})
        )

        result = await self.adapter.exec(sql)

        return {row['field'] for row in result if row['field'] is not None}
