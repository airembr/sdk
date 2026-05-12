from srd.domain.sql import Sql, Param

from airembr.system.adapter.bigdata.general.bd_log_adapter import DbLogAdapter
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.helpers.aggregations import bucket_data
from airembr.model.payload.query_result import QueryResult
from airembr.system.adapter.bigdata.general.utils.mapping import log_mapping
from airembr.system.adapter.bigdata.general.metadata import sys_log as sys_log_metadata
from airembr.core.time.time_converters import pretty_seconds
from airembr.model.system.query.time_range_query import DatetimeRangePayload
from airembr.sdk.common.date import now_in_utc


class StarrocksLogAdapter(DbLogAdapter):

    async def load_log_histogram(self, query: DatetimeRangePayload) -> QueryResult:
        database = current_bd_database_name()

        buckets = 60
        now = now_in_utc().timestamp()
        min_date, max_date = query.get_dates()
        time_span = (max_date - min_date).total_seconds()
        interval = time_span / buckets  # sec

        sys_log = log_mapping()

        sql = (
                Sql()
                + f"SELECT "
                  f"FLOOR(UNIX_TIMESTAMP({sys_log_metadata.DATE}) / {interval}) * {interval} AS ts, "
                  f"COUNT(*) AS count"
                + f"FROM {database}.{sys_log}"
                + f"WHERE {sys_log_metadata.DATE} BETWEEN :min AND :max "
                + f"GROUP BY {sys_log_metadata.DATE}"
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
