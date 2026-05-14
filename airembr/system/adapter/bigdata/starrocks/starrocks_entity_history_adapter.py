from srd.domain.sql import Sql, Param

from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.general.bd_entity_history_adapter import BdEntityHistoryAdapter
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.utils.mapping import entity_history_mapping
from airembr.system.adapter.bigdata.general.helpers.aggregations import bucket_data
from airembr.system.adapter.bigdata.tool.column_mapper import map_to_table_columns
from airembr.model.payload.query_result import QueryResult
from airembr.model.bigdata.flat_ent_history import FlatEntityHistory
from airembr.core.time.time_converters import pretty_seconds

from airembr.model.api.request.time_range import DatetimeRangePayload
from airembr_sdk.core.date import now_in_utc

_ent_history_mapping = entity_history_mapping()

class StarrocksEntityHistoryAdapter(BdEntityHistoryAdapter):


    @staticmethod
    async def extend_observation_context(entities):
        context_entity_rows = map_to_table_columns(entities,
                                                   mapping=_ent_history_mapping)

        return await AdapterRouter().adapter.stream(context_entity_rows, _ent_history_mapping)

    async def load_event_entities_histogram(self,
                                            query: DatetimeRangePayload) -> QueryResult:
        buckets = 60
        now = now_in_utc().timestamp()
        min_date, max_date = query.get_dates()
        time_span = (max_date - min_date).total_seconds()
        interval = time_span / buckets  # sec
        database = current_bd_database_name()
        sys_ent_history = entity_history_mapping()

        sql = (
                Sql()
                + f"SELECT "
                  f"FLOOR(UNIX_TIMESTAMP(`{sys_ent_history | FlatEntityHistory.TS}`) / {interval}) * {interval} AS ts, "
                  f"COUNT(*) AS count"
                + f"FROM {database}.{sys_ent_history}"
                + f"WHERE {sys_ent_history | FlatEntityHistory.TS} BETWEEN :min AND :max "
                + f"GROUP BY {sys_ent_history | FlatEntityHistory.TS}"
                + Param({"min": min_date, "max": max_date})
        )

        result = await self.adapter.exec(sql)

        result = [(int(row.get('ts', 0)), row.get('count', 0)) for row in result]
        buckets = bucket_data(result, min_date, max_date, buckets,
                              lambda bucket_lo, bucket_hi, interval: int(now - bucket_hi))

        x = []
        for span, count in buckets.items():
            pretty_date = f"-{pretty_seconds(span)}"
            pretty_interval = f"{pretty_seconds(interval)}"
            x.append({
                "date": pretty_date,
                "interval": pretty_interval,
                "speed": f"{count / interval if interval > 0 else 0:.3f}/s",
                "collected": count
            })

        return QueryResult(total=len(buckets), result=x, buckets=['collected'])
