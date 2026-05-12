from typing import List, Callable, Optional

from airembr.sdk.common.date import now_in_utc
from airembr.model.bigdata.flat_fact import FlatFact
from airembr.core.time.time_converters import pretty_seconds
from airembr.model.payload.query_result import QueryResult
from airembr.model.system.query.time_range_query import DatetimeRangePayload

from srd.domain.sql import Sql, Param

from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.bd_event_adapter import BdEventAdapter
from airembr.system.adapter.bigdata.general.helpers.filters import within
from airembr.system.adapter.bigdata.starrocks.utils.sql_histogram import event_histogram_sql
from system.driver.result_protocol import ResultProtocol
from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping
from airembr.system.adapter.bigdata.general.helpers.aggregations import bucket_data


class StarrocksEventAdapter(BdEventAdapter):

    async def load_events_histogram(self, query: DatetimeRangePayload) -> QueryResult:
        buckets = 60
        now = now_in_utc().timestamp()
        min_date, max_date = query.get_dates()
        time_span = (max_date - min_date).total_seconds()
        interval = time_span / buckets  # sec

        sql = event_histogram_sql(query)

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

    async def search_all(self, query: DatetimeRangePayload):

        sql_count, sql_fetch = self.search_sql(query)

        records_counts = await self.adapter.exec(sql_count)
        count = records_counts.first().column(0)

        result = await self.adapter.exec(sql_fetch)

        sys_evt = event_mapping()
        return QueryResult(total=count, result=(result >> sys_evt).list(cast_to=dict))

    @staticmethod
    def _yield_processed_rows(result: ResultProtocol, function: Callable, mapping):
        for row in (result >> mapping):
            yield function(row)

    async def search_and_process_all(self, query: DatetimeRangePayload, function: Callable):

        sql_count, sql_fetch = self.search_sql(query)

        records_counts = await self.adapter.exec(sql_count)
        count = records_counts.first().column(0)

        result = await self.adapter.exec(sql_fetch)
        sys_evt = event_mapping()
        return QueryResult(total=count,
                           result=list(self._yield_processed_rows(result, function, sys_evt)))

    async def load_events_by_actor_pks(self,
                                       entity_pks: List[str],
                                       limit: int,
                                       days: Optional[int] = 30,
                                       return_as_storage_result: Optional[bool]=True) -> QueryResult:
        sys_evt = event_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT * FROM {database}.{sys_evt} "
                + f"WHERE {sys_evt | FlatFact.ACTOR_PK} IN :ent_id_col " + Param({"ent_id_col": tuple(entity_pks)})
                + f" AND {sys_evt | FlatFact.METADATA_TIME_INSERT} > {within(f'{days} DAY')} "
                + f"ORDER BY {sys_evt | FlatFact.METADATA_TIME_INSERT} DESC"
                + (bool(limit), f"LIMIT :limit", {"limit": limit})
        )

        result = await self.adapter.exec(sql)
        if return_as_storage_result:
            result = (result >> sys_evt).list(cast_to=dict)
            return QueryResult(total=len(result), result=result)
        return result

    async def load_events_by_object_pks(self,
                                        entity_pks: List[str],
                                        limit: int,
                                        days: Optional[int] = 30,
                                        return_as_storage_result: Optional[bool]=True) -> QueryResult:
        sys_evt = event_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT * FROM {database}.{sys_evt} "
                + f"WHERE {sys_evt | FlatFact.OBJECT_PK} IN :ent_id_col " + Param({"ent_id_col": tuple(entity_pks)})
                + f" AND {sys_evt | FlatFact.METADATA_TIME_INSERT} > {within(f'{days}  DAY')} "
                + f"ORDER BY {sys_evt | FlatFact.METADATA_TIME_INSERT} DESC"
                + (bool(limit), f"LIMIT :limit", {"limit": limit})
        )

        result = await self.adapter.exec(sql)
        if return_as_storage_result:
            result = (result >> sys_evt).list(cast_to=dict)
            return QueryResult(total=len(result), result=result)
        return result

    async def count_export_facts_by_source(self, source_id: str) -> int:
        sql_count = self.count_export_by_source_sql(source_id)
        records_counts = await self.adapter.exec(sql_count)
        return records_counts.first().column(0)

    async def export_observation_by_source(self, source_id: str, start: Optional[int] = None,
                                           limit: Optional[int] = None):
        sql_fetch = self.export_by_source_sql(source_id, start, limit)
        return await self.adapter.exec(sql_fetch)

    async def export_facts_by_source(self, source_id: str, start: Optional[int] = None, limit: Optional[int] = None):
        sql = self.export_facts_by_source_sql(source_id, start, limit)
        return await self.adapter.exec(sql)

    async def export_facts_entities(self, entities: List[str]):
        sql_fetch = self.export_facts_entities_sql(entities)
        return await self.adapter.exec(sql_fetch)
