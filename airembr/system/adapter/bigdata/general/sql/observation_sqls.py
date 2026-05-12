from airembr.model.system.query.time_range_query import DatetimeRangePayload
from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.general.utils.mapping import sys_obs_mapping
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.model.bigdata.flat_obs import FlatObs


def load_observation_by_id_sql(observation_id: str):
    sys_obs = sys_obs_mapping()

    database = current_bd_database_name()
    return (
            Sql()
            + f"SELECT *"
            + f"FROM {database}.{sys_obs} AS o "
            # + f"JOIN {database}.{sys_obs} AS o"
            + f"WHERE o.{sys_obs | FlatObs.ID} = :obs_id"
            + f"ORDER BY o.{sys_obs | FlatObs.METADATA_TIME_INSERT} DESC"
            + Param({"obs_id": observation_id})
    )


def search_observation_by_query_sql(query: DatetimeRangePayload):
    sys_obs = sys_obs_mapping()
    min_date, max_date = query.get_dates()
    database = current_bd_database_name()

    if query.sort is None:
        ts = sys_obs | FlatObs.METADATA_TIME_INSERT
    elif query.sort == 'create':
        ts = sys_obs | FlatObs.METADATA_TIME_CREATE
    else:
        ts = sys_obs | FlatObs.METADATA_TIME_INSERT

    return (
            Sql()
            + f"SELECT * FROM {database}.{sys_obs}"
            + f"WHERE "
            + f"{ts} BETWEEN :min AND :max" + Param({"min": min_date, "max": max_date})
            + (query.where, f"AND {query.where}")
            + f"ORDER BY {ts} DESC"
            + (query.limit, f"LIMIT :limit OFFSET :offset", Param({"offset": query.start, "limit": query.limit}))
    )


def count_observation_by_query_sql(query: DatetimeRangePayload):
    sys_obs = sys_obs_mapping()
    min_date, max_date = query.get_dates()
    database = current_bd_database_name()
    ts = sys_obs | FlatObs.TS

    return (
            Sql()
            + f"SELECT COUNT(*) as \"count\" FROM {database}.{sys_obs}"
            + f"WHERE {ts} BETWEEN :min AND :max" + Param({"min": min_date, "max": max_date})
            + (query.where, f"AND {query.where}")
    )
