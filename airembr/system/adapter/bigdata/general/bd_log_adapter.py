from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from uuid import uuid4

from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.model.payload.query_result import QueryResult
from airembr.model.bigdata.flat_log import FlatLog
from airembr.system.adapter.bigdata.general.utils.mapping import log_mapping
from airembr.system.adapter.bigdata.general.metadata import sys_log as sys_log_metadata

from airembr.model.api.request.time_range import DatetimeRangePayload
from airembr_sdk.core.date import now_in_utc

from srd.domain.column import Count
from srd.domain.select import Select
from srd.domain.sql import Sql, Param


async def _load_by(driver, property, value: str, order: Optional[str] = 'DESC', limit: Optional[int] = None):
    sys_log = log_mapping()

    database = current_bd_database_name()
    sql = (
            Sql()
            + f"SELECT COUNT(*) as count FROM {database}.{sys_log}"
            + f"WHERE {sys_log | property} = :value" + Param({"value": value})
    )

    records_counts = await driver.exec(sql)
    count = records_counts.first().column(0)

    if count == 0:
        return [], 0

    sql = (
            Sql()
            + f"SELECT * FROM {database}.{sys_log}"
            + f"WHERE {sys_log | property} = :value" + Param({"value": value})
            + (bool(order), f"ORDER BY {sys_log | FlatLog.DATE} {order}")
            + (bool(limit), f"LIMIT :limit", Param({"limit": limit}))
    )

    records = await driver.exec(sql)

    return records >> sys_log, count


class DbLogAdapter(AdapterRouter):

    async def search_all(self, query: DatetimeRangePayload):
        sys_log = log_mapping()
        min_date, max_date = query.get_dates()
        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT COUNT(*) as count FROM {database}.{sys_log}"
                + f"WHERE {sys_log_metadata.DATE} BETWEEN :min AND :max" + Param({"min": min_date, "max": max_date})
                + (query.where, f"AND {query.where}")
        )

        records_counts = await self.adapter.exec(sql)
        count = records_counts.first().column(0)

        sql = (
                Sql()
                + f"SELECT * FROM {database}.{sys_log}"
                + f"WHERE {sys_log_metadata.DATE} BETWEEN :min AND :max" + Param({"min": min_date, "max": max_date})
                + (query.where, f"AND {query.where}")
                + f"ORDER BY {sys_log_metadata.DATE} DESC"
                + (query.limit, f"LIMIT :limit OFFSET :offset", Param({"offset": query.start, "limit": query.limit}))
        )

        result = await self.adapter.exec(sql)

        return QueryResult(total=count, result=(result >> sys_log).list(cast_to=dict))

    async def load_entity_logs_by_entity_id(self, entity_name: str, entity_id: str, sort: Optional[str] = "DESC",
                                            limit=30) -> Tuple[List[dict], int]:
        return await _load_by(self.adapter, 'entity.id', entity_id, order=sort, limit=limit)

    # Old
    async def load_logs_by_flow(self, flow_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[
        List[dict], int]:
        return await _load_by(self.adapter, 'flow.id', flow_id, order=sort, limit=limit)

    async def load_logs_by_profile(self, profile_id: str, sort: Optional[str] = "DESC", limit=30) -> Tuple[
        List[dict], int]:
        return await _load_by(self.adapter, 'profile.id', profile_id, order=sort, limit=limit)

    async def load_logs_by_event(self, event_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[
        List[dict], int]:
        return await _load_by(self.adapter, 'event.id', event_id, order=sort, limit=limit)

    async def load_logs_by_node(self, node_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[
        List[dict], int]:
        return await _load_by(self.adapter, 'node.id', node_id, order=sort, limit=limit)

    async def aggr_group_logs_by_level(self, date_from: Optional[datetime] = None) -> Dict[str, int]:
        if date_from is None:
            date_from = now_in_utc() - timedelta(days=30)

        mapping = log_mapping()

        ts_col = mapping.get_column(FlatLog.DATE)
        level_col = mapping.get_column(FlatLog.LEVEL)
        count_col = Count(name="*", alias="count")

        where = f"{~ts_col}>=:date_from"
        params = {"date_from": date_from}

        sql = (Select(mapping.table)
               .columns([level_col, count_col])
               .where(where)
               .group([level_col]))
        result = await self.adapter.query(sql, params)

        return {row[level_col.name]: row[count_col.alias] for row in result}

    async def save_logs(self, logs: List):
        if logs:
            mapping = log_mapping()
            logs = [{**row, "id": str(uuid4())} for row in logs]
            return await self.adapter.stream(logs, mapping)
        return None
