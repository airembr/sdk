from airembr.model.bigdata.flat_fact import FlatFact
from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name


def event_histogram_sql(query) -> Sql:
    buckets = 60
    min_date, max_date = query.get_dates()
    time_span = (max_date - min_date).total_seconds()
    interval = time_span / buckets  # sec
    database = current_bd_database_name()

    sys_evt = event_mapping()
    if query.sort is None:
        ts = sys_evt | FlatFact.METADATA_TIME_CREATE
    elif query.sort == 'create':
        ts = sys_evt | FlatFact.METADATA_TIME_CREATE
    else:
        ts = sys_evt | FlatFact.METADATA_TIME_INSERT

    return (
            Sql()
            + f"SELECT "
              f"FLOOR(UNIX_TIMESTAMP({ts}) / {interval}) * {interval} AS ts, "
              f"COUNT(*) AS count"
            + f"FROM {database}.{sys_evt}"
            + f"WHERE {ts} BETWEEN :min AND :max "
            # + f"GROUP BY {ts}"
            + f"GROUP BY ts"
            + Param({"min": min_date, "max": max_date})
    )