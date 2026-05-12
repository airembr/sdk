from typing import List, Optional, Tuple

from airembr.model.bigdata.flat_ent_history import FlatEntityHistory
from airembr.model.bigdata.flat_fact import FlatFact
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.model.system.query.time_range_query import DatetimeRangePayload

from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name

from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping, entity_history_mapping
from airembr.system.adapter.bigdata.general.helpers.loaders import load


class BdEventAdapter(AdapterRouter):

    # CRUD

    # async def stream_event(self, event_rows: str, timeout: Optional[int] = 5):
    #     mapping = event_mapping()
    #
    #     return await self.stream(event_rows, mapping, timeout)

    async def load_event_by_id(self, event_id: str) -> Optional[FlatFact]:
        sys_evt = event_mapping()

        id = sys_evt.get_column('id')
        condition = f"{~id}=:id"
        params = {"id": event_id}

        records = await load(self.adapter, sys_evt, condition, params=params, cast_to=FlatFact)

        if not records:
            return None

        return records[0]

    async def delete_event_from_db(self, event_id):
        sys_evt = event_mapping()
        database = current_bd_database_name()
        sql = Sql(f"DELETE FROM {database}.{sys_evt} WHERE id=:id") + Param({"id": event_id})

        await self.adapter.exec(sql)

    async def count(self) -> int:
        mapping = event_mapping()
        result = await self.adapter._count(mapping.table)
        return result.first().column(0)

    # GUI

    async def load_events_by_type(self, event_type: str, limit):
        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT type, traits"
                + f"FROM {database}.sys_v_uniq_ent_traits"
                + f"WHERE rel_label = :event_type " + Param({"event_type": event_type})
                + f"LIMIT :limit " + Param({"limit": limit})
        )

        result = await self.adapter.exec(sql)

        return [(row['type'], row['traits']) for row in result]

    async def load_events_by_data_hash(self, data_hash: str, limit=100) -> List[dict[str, str]]:

        sys_evt = event_mapping()
        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT DISTINCT {sys_evt | FlatFact.ID} as id, {sys_evt | FlatFact.REL_LABEL} as type, {sys_evt | FlatFact.METADATA_TIME_CREATE} as create_time"
                + f"FROM {database}.{sys_evt}"
                + f"WHERE {sys_evt | FlatFact.ACTOR_DATA_HASH} = :data_hash "
                + f"OR {sys_evt | FlatFact.OBJECT_DATA_HASH} = :data_hash" + Param({"data_hash": data_hash})
                + "ORDER BY create_time DESC"
                + f"LIMIT :limit " + Param({"limit": limit})
        )
        result = await self.adapter.exec(sql)

        return [{"id": row['id'], "type": row['type'], "ts": row['create_time']} for row in result]

    async def load_unique_event_types(self, limit, entity_type: str = None) -> List[str]:
        # It loads unique event types

        sys_evt = event_mapping()
        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT DISTINCT {sys_evt | FlatFact.REL_LABEL} as type"
                + f"FROM {database}.{sys_evt}"
                + (bool(entity_type), f"WHERE {sys_evt | FlatFact.ACTOR_TYPE} = :entity_type "
                                      f"OR {sys_evt | FlatFact.OBJECT_TYPE} = :entity_type",
                   Param({"entity_type": entity_type}))
                + f"LIMIT :limit " + Param({"limit": limit})
        )
        result = await self.adapter.exec(sql)

        return [row['type'] for row in result]

    async def load_unique_event_actor_types(self, limit: int, entity_type: str = None) -> List[str]:
        # it loads unique event actor types
        sys_evt = event_mapping()
        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT DISTINCT {sys_evt | FlatFact.ACTOR_TYPE} as actor_type"
                + f"FROM {database}.{sys_evt}"
                + (bool(entity_type), f"WHERE {sys_evt | FlatFact.ACTOR_TYPE} = :entity_type ",
                   Param({"entity_type": entity_type}))
                + f"LIMIT :limit " + Param({"limit": limit})
        )
        result = await self.adapter.exec(sql)

        return [row['actor_type'] for row in result]

    def search_sql(self, query: DatetimeRangePayload):
        sys_evt = event_mapping()
        min_date, max_date = query.get_dates()
        database = current_bd_database_name()
        if query.sort is None:
            ts = sys_evt | FlatFact.METADATA_TIME_CREATE
        elif query.sort == 'create':
            ts = sys_evt | FlatFact.METADATA_TIME_CREATE
        else:
            ts = sys_evt | FlatFact.METADATA_TIME_INSERT

        sql_count = (
                Sql()
                + f"SELECT COUNT(*) as \"count\" FROM {database}.{sys_evt}"
                + f"WHERE {ts} BETWEEN :min AND :max" + Param({"min": min_date, "max": max_date})
                + (query.where, f"AND {query.where}")
        )

        sql_fetch = (
                Sql()
                + f"SELECT * FROM {database}.{sys_evt}"
                + f"WHERE "
                + f"{ts} BETWEEN :min AND :max" + Param({"min": min_date, "max": max_date})
                + (query.where, f"AND {query.where}")
                + f"ORDER BY {ts} DESC"
                + (query.limit, f"LIMIT :limit OFFSET :offset", Param({"offset": query.start, "limit": query.limit}))
        )

        return sql_count, sql_fetch

    def count_export_by_source_sql(self, source_id: str):
        sys_evt = event_mapping()

        database = current_bd_database_name()

        return (
                Sql()
                + f"SELECT COUNT(*) as \"count\" FROM {database}.{sys_evt}"
                + f"WHERE {sys_evt | FlatFact.SOURCE_ID} = :source_id" + Param({"source_id": source_id})
        )

    def export_by_source_sql(self, source_id: str, start: Optional[int] = None, limit: Optional[int] = None):
        sys_evt = event_mapping()
        sys_ent_history = entity_history_mapping()

        database = current_bd_database_name()

        return (
                Sql()
                + f"SELECT ev.*, "
                  f"ah.{sys_ent_history | FlatEntityHistory.ENTITY_TRAITS} AS actor_traits, "
                  f"ah.{sys_ent_history | FlatEntityHistory.ENTITY_LABEL} AS actor_label, "
                  f"oh.{sys_ent_history | FlatEntityHistory.ENTITY_TRAITS} AS object_traits, "
                  f"oh.{sys_ent_history | FlatEntityHistory.ENTITY_LABEL} AS object_label, "
                  f"rh.{sys_ent_history | FlatEntityHistory.ENTITY_TRAITS} AS rel_traits, "
                  f"rh.{sys_ent_history | FlatEntityHistory.ENTITY_LABEL} AS rel_label "
                + f"FROM {database}.{sys_evt} As ev"
                + f"JOIN {database}.{sys_ent_history} AS ah"
                + f"  ON ah.{sys_ent_history | FlatEntityHistory.ENTITY_PK}=ev.{sys_evt | FlatFact.ACTOR_PK} "
                + f"   AND ah.{sys_ent_history | FlatEntityHistory.DATA_HASH}=ev.{sys_evt | FlatFact.ACTOR_DATA_HASH} "
                + f"JOIN {database}.{sys_ent_history} AS oh"
                + f"  ON oh.{sys_ent_history | FlatEntityHistory.ENTITY_PK}=ev.{sys_evt | FlatFact.OBJECT_PK} "
                + f"   AND oh.{sys_ent_history | FlatEntityHistory.DATA_HASH}=ev.{sys_evt | FlatFact.OBJECT_DATA_HASH} "
                + f"JOIN {database}.{sys_ent_history} AS rh"
                + f"  ON rh.{sys_ent_history | FlatEntityHistory.ENTITY_PK}=ev.{sys_evt | FlatFact.REL_PK} "
                + f"   AND rh.{sys_ent_history | FlatEntityHistory.DATA_HASH}=ev.{sys_evt | FlatFact.REL_DATA_HASH} "

                + f"WHERE {sys_evt | FlatFact.SOURCE_ID} = :source_id" + Param({"source_id": source_id})
                + f"ORDER BY {sys_evt | FlatFact.METADATA_TIME_CREATE} DESC"
                + (limit, f"LIMIT :limit OFFSET :offset", Param({"offset": start, "limit": limit}))
        )

    def export_facts_by_source_sql(self, source_id: str, start: Optional[int] = None, limit: Optional[int] = None):
        sys_evt = event_mapping()
        database = current_bd_database_name()

        return (
                Sql()
                + f"SELECT *"
                + f"FROM {database}.{sys_evt} As ev"
                + f"WHERE {sys_evt | FlatFact.SOURCE_ID} = :source_id" + Param({"source_id": source_id})
                + f"ORDER BY {sys_evt | FlatFact.METADATA_TIME_CREATE} DESC"
                + (limit, f"LIMIT :limit OFFSET :offset", Param({"offset": start, "limit": limit}))
        )

    def export_facts_entities_sql(self, entities: List[str]):
        sys_ent_history = entity_history_mapping()
        database = current_bd_database_name()

        return (
                Sql()
                + f"SELECT *"
                + f"FROM {database}.{sys_ent_history}"
                + f"WHERE {sys_ent_history | FlatEntityHistory.ENTITY_HID} IN :entities" + Param({"entities": tuple(entities)})
        )
