from typing import Set, Tuple, Dict, List, Optional

from srd.domain.sql import Sql, Param

from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.utils.mapping import entity_history_mapping, entity_property
from airembr.model.payload.query_result import QueryResult
from airembr.model.bigdata.flat_ent_history import FlatEntityHistory
from airembr.model.bigdata.flat_ent_property import FlatEntityProperty

from airembr.model.api.request.time_range import DatetimeRangePayload


class BdEntityHistoryAdapter(AdapterRouter):

    async def load_event_entity_types(self, context: str = None) -> Set[Tuple[str, str]]:
        sys_ent_history = entity_history_mapping()

        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT DISTINCT {sys_ent_history | FlatEntityHistory.CONTEXT} as context,"
                  f"{sys_ent_history | FlatEntityHistory.ENTITY_TYPE} as entity_type "
                + f"FROM {database}.{sys_ent_history}"
                + (bool(context), f"WHERE {sys_ent_history | FlatEntityHistory.CONTEXT} = :context",
                   Param({"context": context}))
                + f"ORDER BY entity_type, context DESC"
                + f"LIMIT 100"
        )

        result = await self.adapter.exec(sql)

        return {(row['entity_type'], row['context']) for row in result}

    async def load_event_entity_observer_pks(self) -> List[Dict[str, str]]:
        sys_ent_history = entity_history_mapping()
        sys_ent_property = entity_property()

        database = current_bd_database_name()

        sql = (
                Sql()
                + f"WITH observers as ("
                + f"SELECT DISTINCT e.{sys_ent_history | FlatEntityHistory.OBSERVER_PK} as observer_pk"
                + f"FROM {database}.{sys_ent_history} e)"

                + f"SELECT DISTINCT observers.observer_pk as \"pk\", p.{sys_ent_property | FlatEntityProperty.VALUE} as \"label\" FROM observers "
                + f"LEFT JOIN {database}.{sys_ent_property} p ON observers.observer_pk = p.{sys_ent_property | FlatEntityProperty.PK}"
                + f"AND p.{sys_ent_property | FlatEntityProperty.NAME} = 'name'"  # name property is required
                + "LIMIT 1000"
        )

        result = await self.adapter.exec(sql)

        return [{"id": row['pk'], "name": row['label']} for row in result]

    async def load_entity_history_by_id(self, entity_id: Optional[str] = None, observer_pk: Optional[str] = None,
                                        order: str = 'ASC') -> Set[Tuple[str, str]]:
        sys_ent_history = entity_history_mapping()

        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT * "
                + f"FROM {database}.{sys_ent_history}"
                + f"WHERE {sys_ent_history | FlatEntityHistory.ENTITY_ID} = :entity_id"
                + (bool(observer_pk), f" AND {sys_ent_history | FlatEntityHistory.OBSERVER_PK} = :observer_pk",
                   Param({"observer_pk": observer_pk}))
                + Param({"entity_id": entity_id})
                + f"ORDER BY {sys_ent_history | FlatEntityHistory.TIME_CREATE} {order}"
                + f"LIMIT 25"
        )

        result = await self.adapter.exec(sql)

        return (result >> sys_ent_history).list()

    async def load_event_entities(self, query: DatetimeRangePayload) -> QueryResult:
        sys_ent_history = entity_history_mapping()

        min_date, max_date = query.get_dates()

        query_where = query.where.strip()
        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT COUNT(*) FROM {database}.{sys_ent_history}"
                + f"WHERE {sys_ent_history | FlatEntityHistory.TS} BETWEEN :min AND :max"
                + Param({"min": min_date, "max": max_date})
                + (bool(query_where), f" AND {query_where}")
        )

        records_counts = await self.adapter.exec(sql)
        count = records_counts.first().column(0)

        sql = (
                Sql()
                + f"SELECT * FROM {database}.{sys_ent_history}"
                + f"WHERE {sys_ent_history | FlatEntityHistory.TS} BETWEEN :min AND :max"
                + Param({"min": min_date, "max": max_date})
                + (bool(query_where), f" AND {query_where}")
                + f"ORDER BY {sys_ent_history | FlatEntityHistory.TS} DESC"
                + (
                    bool(query.limit), f"LIMIT :limit OFFSET :offset",
                    Param({"limit": query.limit, "offset": query.start}))
        )

        result = await self.adapter.exec(sql)

        return QueryResult(total=count, result=(result >> sys_ent_history).list(cast_to=dict))
