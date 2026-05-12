from srd.domain.sql import Sql, Param

from airembr.model.bigdata.flat_obs import FlatObs
from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping, sys_obs_mapping
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name


def observation_histogram_sql(query) -> Sql:
    buckets = 60
    min_date, max_date = query.get_dates()
    time_span = (max_date - min_date).total_seconds()
    interval = time_span / buckets  # sec
    database = current_bd_database_name()

    sys_obs = sys_obs_mapping()
    if query.sort is None:
        ts = sys_obs | FlatObs.METADATA_TIME_CREATE
    elif query.sort == 'create':
        ts = sys_obs | FlatObs.METADATA_TIME_CREATE
    else:
        ts = sys_obs | FlatObs.METADATA_TIME_INSERT

    return (
            Sql()
            + f"SELECT "
              f"FLOOR(UNIX_TIMESTAMP({ts}) / {interval}) * {interval} AS timestamp, "
              f"COUNT(*) AS count"
            + f"FROM {database}.{sys_obs}"
            + f"WHERE {ts} BETWEEN :min AND :max "
            + f"GROUP BY timestamp"
            + Param({"min": min_date, "max": max_date})
    )
