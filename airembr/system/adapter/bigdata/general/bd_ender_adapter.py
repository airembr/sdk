from datetime import datetime
from typing import Optional, List

from durable_dot_dict.collection import DotDictStream

from airembr.model.bigdata.flat_ent_2_text import FlatEnt2Text
from airembr.model.bigdata.flat_ent_state import FlatEntityState
from airembr.model.bigdata.flat_text import FlatText
from airembr_sdk.core.date import now_in_utc
from airembr.model.api.request.time_range import DatetimeRangePayload

from airembr.model.bigdata.flat_ent_2_obs import FlatEntity2Observation
from airembr.model.bigdata.flat_fact import FlatFact
from airembr.model.bigdata.flat_obs import FlatObs
from airembr.model.bigdata.flat_ent_history import FlatEntityHistory
from airembr.core.time.time_converters import pretty_seconds
from airembr.model.bigdata.flat_event_job import FlatEventJob
from airembr.model.bigdata.flat_obs_trigger import FlatObsTrigger
from airembr.model.payload.query_result import QueryResult
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.general.helpers.aggregations import bucket_data
from airembr.system.adapter.bigdata.general.sql.histogram import observation_histogram_sql
from airembr.system.adapter.bigdata.general.sql.observation_sqls import search_observation_by_query_sql, \
    count_observation_by_query_sql, load_observation_by_id_sql
from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping, sys_observation_trigger, \
    entity_history_mapping, \
    event_job_mapping, sys_obs_mapping, sys_ent_2_obs, sys_ent_state, sys_ent_2_text_mapping, sys_text_mapping
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name

from srd.domain.result import Row
from srd.domain.sql import Sql, Param


class BdObservationAdapter(AdapterRouter):

    async def stream_ended_observations(self, rows):
        sys_obs = sys_observation_trigger()
        return await self.adapter.stream(rows, sys_obs)

    async def load_ending_observations(self, trigger_id: str, observation_labels: List[str] = None, inactive=60) -> \
            Optional[Row]:
        sys_evt = event_mapping()
        sys_obs_trigger = sys_observation_trigger()

        database = current_bd_database_name()
        sql = (
                Sql()
                + "WITH obs_end_ts AS ("
                + f"SELECT ev.obs_id AS obs_id, MAX(ev.{sys_evt | FlatFact.METADATA_TIME_INSERT}) as last_ts"
                + f"FROM {database}.{sys_evt} ev"
                + f"WHERE ev.{sys_evt | FlatFact.METADATA_TIME_INSERT} + INTERVAL :inactive MINUTE < NOW()"
                + (observation_labels is not None, f"AND ev.{sys_evt | FlatFact.OBS_LABEL} IN :observation_labels",
                   Param({"observation_labels": tuple(observation_labels)}))
                + f"GROUP BY ev.{sys_evt | FlatFact.OBS_ID}"
                + ")"
                + f"SELECT e.*, obs_ended.{sys_obs_trigger | FlatObsTrigger.TS_END} as obs_end_ts"
                + f"FROM obs_end_ts e"
                + f"LEFT JOIN {database}.{sys_obs_trigger} AS obs_ended "
                + f"ON e.{sys_evt | FlatFact.OBS_ID} = obs_ended.{sys_obs_trigger | FlatObsTrigger.OBS_ID} AND obs_ended.{sys_obs_trigger | FlatObsTrigger.TRIGGER_ID} = :trigger_id"
                + f"WHERE obs_ended.{sys_obs_trigger | FlatObsTrigger.TS_END} < e.last_ts OR obs_ended.{sys_obs_trigger | FlatObsTrigger.TS_END} IS NULL"
                + Param({"inactive": inactive, "trigger_id": trigger_id})
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result.list()

    async def load_observations_by_ids(self, ids: List[str]) -> Optional[Row]:
        sys_evt = event_mapping()
        sys_ent_history = entity_history_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT fact.actor_type, fact.actor_pk, actor.entity_traits as actor_traits, fact.rel_label, fact.object_type, fact.object_pk, object.entity_traits as object_traits"
                + f"FROM {database}.{sys_evt} AS fact "

                + f"LEFT JOIN {database}.{sys_ent_history} AS actor ON actor.{sys_ent_history | FlatEntityHistory.ENTITY_PK} = fact.{sys_evt | FlatFact.ACTOR_PK} AND actor.{sys_ent_history | FlatEntityHistory.DATA_HASH} = fact.{sys_evt | FlatFact.ACTOR_DATA_HASH}"
                + f"LEFT JOIN {database}.{sys_ent_history} AS object ON object.{sys_ent_history | FlatEntityHistory.ENTITY_PK} = fact.{sys_evt | FlatFact.OBJECT_PK} AND object.{sys_ent_history | FlatEntityHistory.DATA_HASH} = fact.{sys_evt | FlatFact.OBJECT_DATA_HASH}"

                + f"WHERE fact.{sys_evt | FlatFact.OBS_ID} in :ids"
                + f"ORDER BY fact.{sys_evt | FlatFact.METADATA_TIME_CREATE} ASC"
                + Param({"ids": ids})
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result

    async def load_all_unprocessed_events(self, trigger_id: str,
                                          actor_type: str = None,
                                          event_type: str = None,
                                          after_sec_time: int = 0,
                                          source_id: str = None,
                                          since: Optional[datetime] = None) -> DotDictStream:
        sys_fact = event_mapping()
        sys_evt_job = event_job_mapping()
        sys_ent_history = entity_history_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT fact.*, actor.entity_traits as actor_traits, rel.entity_traits as rel_traits, obj.entity_traits as object_traits"
                + f"FROM {database}.{sys_fact} AS fact"
                + f"LEFT JOIN {database}.{sys_evt_job} AS job ON job.{sys_evt_job | FlatEventJob.REL_ID}=fact.{sys_fact | FlatFact.ID} AND job.{sys_evt_job | FlatEventJob.JOB_ID}=:trigger_id"
                + Param({"trigger_id": trigger_id})
                + f"  LEFT JOIN {database}.{sys_ent_history} actor "
                + f"   ON actor.{sys_ent_history | FlatEntityHistory.ENTITY_ID} = fact.{sys_fact | FlatFact.ACTOR_ID}"
                + f"   AND actor.{sys_ent_history | FlatEntityHistory.DATA_HASH} = fact.{sys_fact | FlatFact.ACTOR_DATA_HASH}"
                # We must join relation by rel_id and rel_data_hash
                + f"  LEFT JOIN {database}.{sys_ent_history} rel "
                + f"   ON rel.{sys_ent_history | FlatEntityHistory.ENTITY_ID} = fact.{sys_fact | FlatFact.REL_ID}"
                + f"   AND rel.{sys_ent_history | FlatEntityHistory.DATA_HASH} = fact.{sys_fact | FlatFact.REL_DATA_HASH}"
                # We must join object by object_id and object_data_hash
                + f"  LEFT JOIN {database}.{sys_ent_history} obj "
                + f"   ON obj.{sys_ent_history | FlatEntityHistory.ENTITY_ID} = fact.{sys_fact | FlatFact.OBJECT_ID}"
                + f"   AND obj.{sys_ent_history | FlatEntityHistory.DATA_HASH} = fact.{sys_fact | FlatFact.OBJECT_DATA_HASH}"
                + f"WHERE job.job_id IS NULL"
                # Conditions
                + (bool(since), f"AND fact.{sys_fact | FlatFact.METADATA_TIME_INSERT} > :since",
                   Param({"since": since}))
                + (bool(actor_type), f"AND fact.{sys_fact | FlatFact.ACTOR_TYPE} = :actor_type",
                   Param({"actor_type": actor_type}))
                + (bool(event_type), f"AND fact.{sys_fact | FlatFact.REL_LABEL} = :event_type",
                   Param({"event_type": event_type}))
                + (bool(source_id), f"AND fact.{sys_fact | FlatFact.SOURCE_ID} = :source_id",
                   Param({"source_id": source_id}))
                + (bool(after_sec_time),
                   f"AND  NOW() >= fact.{sys_fact | FlatFact.METADATA_TIME_INSERT} + INTERVAL :after_sec_time SECOND",
                   Param({"after_sec_time": after_sec_time}))

        )

        result = await self.adapter.exec(sql)
        mapping = sys_fact.get_property_to_column()
        mapping['actor.traits'] = 'actor_traits'
        mapping['object.traits'] = 'object_traits'
        mapping['rel.traits'] = 'rel_traits'
        return result >> mapping

    async def load_observations_by_id(self, obs_id: str, start: int = 0, limit: int = 100) -> Optional[DotDictStream]:
        sys_evt = event_mapping()
        sys_ent_history = entity_history_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT "
                  "fact.*, actor.entity_traits as actor_traits, rel.entity_traits as rel_traits, object.entity_traits as object_traits"
                + f"FROM {database}.{sys_evt} AS fact "

                + f" LEFT JOIN {database}.{sys_ent_history} AS actor "
                + f"   ON actor.{sys_ent_history | FlatEntityHistory.ENTITY_PK} = fact.{sys_evt | FlatFact.ACTOR_PK} "
                + f"   AND actor.{sys_ent_history | FlatEntityHistory.DATA_HASH} = fact.{sys_evt | FlatFact.ACTOR_DATA_HASH}"
                # We must join relation by rel_id and rel_data_hash
                + f" LEFT JOIN {database}.{sys_ent_history} rel "
                + f"   ON rel.{sys_ent_history | FlatEntityHistory.ENTITY_ID} = fact.{sys_evt | FlatFact.REL_ID}"
                + f"   AND rel.{sys_ent_history | FlatEntityHistory.DATA_HASH} = fact.{sys_evt | FlatFact.REL_DATA_HASH}"

                + f"LEFT JOIN {database}.{sys_ent_history} AS object "
                + f"  ON object.{sys_ent_history | FlatEntityHistory.ENTITY_PK} = fact.{sys_evt | FlatFact.OBJECT_PK} "
                + f"  AND object.{sys_ent_history | FlatEntityHistory.DATA_HASH} = fact.{sys_evt | FlatFact.OBJECT_DATA_HASH}"

                + f"WHERE fact.{sys_evt | FlatFact.OBS_ID} = :obs_id"
                + f"ORDER BY fact.{sys_evt | FlatFact.METADATA_TIME_CREATE} ASC"
                + Param({"obs_id": obs_id})
                + f"LIMIT :start, :limit"
                + Param({"start": start, "limit": limit})
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        mapping = sys_evt.get_property_to_column()
        mapping['actor.traits'] = 'actor_traits'
        mapping['object.traits'] = 'object_traits'
        mapping['rel.traits'] = 'rel_traits'
        return result >> mapping

    async def load_observation_by_id(self, obs_id: str) -> Optional[DotDictStream]:
        sql = load_observation_by_id_sql(obs_id)

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result

    async def load_facts_by_observation_id(self, obs_id: str, start: int, limit: int) -> Optional[DotDictStream]:
        sys_evt = event_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT fact.*"
                + f"FROM {database}.{sys_evt} AS fact "
                + f"WHERE fact.{sys_evt | FlatFact.OBS_ID} = :obs_id"
                + f"ORDER BY fact.{sys_evt | FlatFact.METADATA_TIME_CREATE} ASC, fact.{sys_evt | FlatFact.METADATA_ORDER} ASC"
                + f"LIMIT :start, :limit"
                + Param({"obs_id": obs_id, "start": start, "limit": limit})
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result >> sys_evt

    async def delete_observation_by_id(self, obs_id: str):
        sys_evt = event_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"DELETE"
                + f"FROM {database}.{sys_evt}"
                + f"WHERE {sys_evt | FlatFact.OBS_ID} = :obs_id"
                + Param({"obs_id": obs_id})
        )

        await self.adapter.exec(sql)

    async def count_observations(self) -> int:
        sys_obs_map = sys_obs_mapping()
        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT COUNT(*) as count"
                + f"FROM {database}.{sys_obs_map}"
        )

        result = await self.adapter.exec(sql)
        return result.first().column(0)

    async def count_observations_by_query(self, query: DatetimeRangePayload) -> int:
        sql = count_observation_by_query_sql(query)
        result = await self.adapter.exec(sql)
        return result.first().column(0)

    async def load_observations_by_query(self, query: DatetimeRangePayload) -> Optional[DotDictStream]:
        sys_obs_map = sys_obs_mapping()
        sql = search_observation_by_query_sql(query)

        result = await self.adapter.exec(sql)
        if not result:
            return None
        return result >> sys_obs_map

    async def load_observations(self) -> Optional[DotDictStream]:
        sys_obs_map = sys_obs_mapping()
        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT *"
                + f"FROM {database}.{sys_obs_map}"
                + f"ORDER BY ts DESC"
                + f"LIMIT 100"
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None
        return result >> sys_obs_map

    async def load_entity_descriptions(self, entity_pks: List[str], limit: int = 1000) -> Optional[DotDictStream]:
        _sys_ent_2_text = sys_ent_2_text_mapping()
        _sys_text = sys_text_mapping()
        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT DISTINCT e2t.{_sys_ent_2_text |FlatEnt2Text.TS} AS ts, e2t.{_sys_ent_2_text |FlatEnt2Text.ENTITY_PK} AS entity_pk, e2t.{_sys_ent_2_text |FlatEnt2Text.ORIGIN}, t.{_sys_text | FlatText.TEXT} AS text_string"
                + f"FROM {database}.{_sys_ent_2_text} AS e2t"
                + f"JOIN {database}.{_sys_text} AS t "
                  f"  ON e2t.{_sys_ent_2_text | FlatEnt2Text.TEXT_ID}= t.{_sys_text | FlatText.ID}"
                + f"WHERE e2t.{_sys_ent_2_text |FlatEnt2Text.ENTITY_PK} IN :entity_pks"
                + "LIMIT :limit"
                + Param({"entity_pks": tuple(entity_pks), "limit": limit})
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result

    async def load_observations_entity_states_by_observation_id(self, obs_ids: List[str], order_by: Optional[str] = None) -> Optional[DotDictStream]:
        _sys_ent_2_obs = sys_ent_2_obs()
        _sys_ent_2_text = sys_ent_2_text_mapping()
        _sys_ent_state = sys_ent_state()
        _sys_obs = sys_obs_mapping()
        database = current_bd_database_name()

        if not order_by:
            order_by = "o.metadata_time_create DESC"

        sql = (
                Sql()
                + f"SELECT e2o.*"
                + ", es.traits, es.stitch_ts"
                + ", o.description, o.summary, o.label, o.metadata_time_create, o.metadata_time_insert"
                + f"FROM {database}.{_sys_ent_2_obs} AS e2o"
                + f"JOIN {database}.{_sys_obs} AS o "
                  f"  ON o.{_sys_obs | FlatObs.ID}= e2o.{_sys_ent_2_obs | FlatEntity2Observation.OBSERVATION_ID}"
                + f"LEFT JOIN {database}.{_sys_ent_state} AS es"
                  f"  ON es.{_sys_ent_state | FlatEntityState.PK}= e2o.{_sys_ent_2_obs | FlatEntity2Observation.ENTITY_PK}"
                + f"WHERE e2o.{_sys_ent_2_obs | FlatEntity2Observation.OBSERVATION_ID} IN :obs_ids"
                + f"ORDER BY {order_by}"
                + "LIMIT 500"
                + Param({"obs_ids": tuple(obs_ids)})
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result


    async def load_observations_entities_by_observation_id(self, obs_ids: List[str], order_by: Optional[str] = None) -> Optional[DotDictStream]:

        # No connection to observations as there may be many, with different descriptions.

        _sys_ent_2_obs = sys_ent_2_obs()
        _sys_ent_2_text = sys_ent_2_text_mapping()
        _sys_ent_state = sys_ent_state()
        _sys_obs = sys_obs_mapping()
        database = current_bd_database_name()

        if not order_by:
            order_by = "o.metadata_time_create DESC"

        sql = (
                Sql()
                + f"SELECT e2o.*"
                + ", es.traits, es.stitch_ts"
                + f"FROM {database}.{_sys_ent_2_obs} AS e2o"
                + f"LEFT JOIN {database}.{_sys_ent_state} AS es"
                  f"  ON es.{_sys_ent_state | FlatEntityState.PK}= e2o.{_sys_ent_2_obs | FlatEntity2Observation.ENTITY_PK}"
                + f"WHERE e2o.{_sys_ent_2_obs | FlatEntity2Observation.OBSERVATION_ID} IN :obs_ids"
                + f"ORDER BY {order_by}"
                + "LIMIT 500"
                + Param({"obs_ids": tuple(obs_ids)})
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result

    async def load_facts_by_observation_ids_and_entity_pks(self,
                                                           obs_ids: List[str],
                                                           entity_pks: List[str],
                                                           start: int,
                                                           limit: int) \
            -> Optional[DotDictStream]:
        sys_evt = event_mapping()
        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT *"
                + f"FROM {database}.{sys_evt} AS fact "
                + f"WHERE fact.{sys_evt | FlatFact.OBS_ID} IN :obs_ids AND ({sys_evt | FlatFact.ACTOR_PK} IN :entity_pks OR {sys_evt | FlatFact.OBJECT_PK} IN :entity_pks) "
                + f"LIMIT :start, :limit"
                + Param({"entity_pks": tuple(entity_pks),
                         "obs_ids": tuple(obs_ids),
                         "start": start,
                         "limit": limit
                         })
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result >> sys_evt

    async def load_facts_by_observation_ids(self,
                                            obs_ids: List[str],
                                            start: int,
                                            limit: int) \
            -> Optional[DotDictStream]:
        sys_evt = event_mapping()
        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT *"
                + f"FROM {database}.{sys_evt} AS fact "
                + f"WHERE fact.{sys_evt | FlatFact.OBS_ID} IN :obs_ids"
                + f"LIMIT :start, :limit"
                + Param({"obs_ids": tuple(obs_ids),
                         "start": start,
                         "limit": limit
                         })
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result >> sys_evt

    async def load_observations_histogram(self, query: DatetimeRangePayload) -> QueryResult:
        buckets = 60
        now = now_in_utc().timestamp()
        min_date, max_date = query.get_dates()
        time_span = (max_date - min_date).total_seconds()
        interval = time_span / buckets  # sec

        sql = observation_histogram_sql(query)

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

    async def load_observations_by_entity_pk(self, entity_pk: str) -> Optional[DotDictStream]:
        _sys_ent_2_obs = sys_ent_2_obs()
        _sys_obs = sys_obs_mapping()
        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT e2o.*, o.description, o.summary, o.label, o.metadata_time_create, o.metadata_time_insert"
                + f"FROM {database}.{_sys_ent_2_obs} AS e2o"
                + f"JOIN {database}.{_sys_obs} AS o ON o.{_sys_obs | FlatObs.ID}= e2o.{_sys_ent_2_obs | FlatEntity2Observation.OBSERVATION_ID}"
                + f"WHERE e2o.{_sys_ent_2_obs | FlatEntity2Observation.ENTITY_PK} = :entity_pk"
                + Param({"entity_pk": entity_pk})
                + f"ORDER BY metadata_time_create DESC"
                + "LIMIT 500"
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None

        return result
