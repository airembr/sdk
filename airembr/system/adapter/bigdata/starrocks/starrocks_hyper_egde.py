import json
import itertools
from typing import List, Optional, Dict

from pydantic import BaseModel
from enum import IntEnum

from srd.domain.sql import Sql, Param
from airembr.sdk.ai.response.memory_response import TimeStats
from airembr.model.system.meta_language.meta_lang_model import MetaLangEntityBase
from airembr.core.time.timer import timer
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.starrocks.utils.sql_entity_search import sql_entity_by_properties
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.utils.mapping import observation_2_entity_mapping


def cartesian_product_size(data: dict):
    size = 0
    for v in data.values():
        if size == 0:
            size = len(v)
        else:
            size *= len(v)
    return size


def cartesian_product_tuples(data: dict):
    return list(itertools.product(*data.values()))


def all_entities(data: dict):
    all = []
    for v in data.values():
        all.extend(v)
    return all


def _parse_json_callable(i):
    try:
        return json.loads(i) if i is not None else None
    except Exception as e:
        return '<json-parse-error>'


def _structure_facts(records):
    return (
            records.to_dot_dict_stream() >> {
        "id": "id",
        "obs.time.create": "metadata_time_create",
        "obs.time.insert": "metadata_time_insert",
        "tags": "tags",
        "subjective": "subjective",
        "obs.id": "obs_id",
        "obs.label": "obs_label",
        "source.id": "source_id",
        "observer.id": "observer_id",
        "observer.pk": "observer_pk",
        "observer.type": "observer_type",
        "observer.role": "observer_role",
        "actor.id": "actor_id",
        "actor.pk": "actor_pk",
        "actor.iid": "actor_iid",
        "actor.type": "actor_type",
        "actor.role": "actor_role",
        "actor.state.ts": "actor_state_ts",
        "actor.traits": "actor_traits",
        "rel.id": "rel_id",
        "rel.pk": "rel_pk",
        "rel.type": "rel_type",
        "rel.label": "rel_label",
        "object.id": "object_id",
        "object.pk": "object_pk",
        "object.iid": "object_iid",
        "object.type": "object_type",
        "object.role": "object_role",
        "object.state.ts": "object_state_ts",
        "object.traits": "object_traits",
        "semantic.summary": "semantic_summary",
        "semantic.description": "semantic_description",
        "metadata.context.entities": "metadata_context_entities"
    } << {
                "tags": _parse_json_callable,
                "actor.traits": _parse_json_callable,
                "object.traits": _parse_json_callable,
                "metadata.context.entities": _parse_json_callable
            }).list()


class GraphResponseStatusEnum(IntEnum):
    OK = 200
    TOO_MANY_FACTS = 413
    NOT_FOUND = 404


class GraphResponse(BaseModel):
    status: GraphResponseStatusEnum
    reason: str
    observations: List[Dict]
    facts: List[Dict]
    stats: TimeStats


class BdHyperEdgeAdapter(AdapterRouter):

    async def find_hyper_edge(self,
                              query: List[MetaLangEntityBase],
                              observer_pk: Optional[str] = None,
                              page: Optional[int] = 0) -> GraphResponse:
        sys_obs_2_entity = observation_2_entity_mapping()

        database = current_bd_database_name()
        stats = TimeStats()

        with timer() as entity_search_timer:
            entities_in_context = {}
            distinct_entity_types = set()
            found_entities_as_requested = 0  # Some entities may be requested with properties but can not be found

            for no, entity in enumerate(query):
                entity_type = entity.type.lower()
                entity_properties = entity.properties
                sql = sql_entity_by_properties(entity_properties, entity_type, observer_pk)
                sql += Sql("SELECT DISTINCT entity_pk FROM queried_entity_properties")

                print(1, sql.literal())

                records = await self.adapter.exec(sql)
                record_pks = [record['entity_pk'] for record in records.list()]

                if len(record_pks) == 0:
                    # No entities found with full search (entity_type + entity_properties)
                    if entity_properties:
                        # There were properties so lets try a search without them.
                        if found_entities_as_requested > 0:
                            # But only if there is at least one entity that was found as requested.
                            # Lets make broader search ONLY for entity type without properties.
                            sql = sql_entity_by_properties([], entity_type, observer_pk)
                            sql += Sql("SELECT DISTINCT entity_pk FROM queried_entity_properties")
                            print(2, sql.literal())

                            records = await self.adapter.exec(sql)
                            record_pks = [record['entity_pk'] for record in records.list()]
                else:
                    found_entities_as_requested += 1

                entities_in_context[(entity_type, no)] = record_pks

                print(entities_in_context)

                distinct_entity_types.add(entity_type)

            number_of_edges = cartesian_product_size(entities_in_context)
            if number_of_edges > 100:
                return GraphResponse(
                    status=GraphResponseStatusEnum.TOO_MANY_FACTS,
                    reason=f"You need to be more precise I have memorized over {number_of_edges} facts that could answer your question.",
                    observations=[],
                    facts=[],
                    stats=stats
                )

        stats.entity_search = entity_search_timer.elapsed

        with timer() as hyper_edge_timer:
            mix_of_entities_to_search = cartesian_product_tuples(entities_in_context)

            if not mix_of_entities_to_search:
                # No entities in the same context.

                # We have 2 options:
                # - Search by each entity one by one. There may be not related.
                # - Or say I do not recall this. (This is what we currently do)
                return GraphResponse(
                    status=GraphResponseStatusEnum.NOT_FOUND,
                    reason=f"I can not recall this. I have not found {' AND '.join(distinct_entity_types)} in one observation.",
                    observations=[],
                    facts=[],
                    stats=stats
                )

            x = []
            for one_set in mix_of_entities_to_search:
                if len(one_set) == 1:
                    x.append(f"o.entity_id = '{one_set[0]}'")
                else:
                    x.append(f"o.entity_id IN {one_set}")

            sql_where_inject = " OR ".join(x)

            # Context - Hyper edge
            sql = (
                    Sql()
                    + f"SELECT o.observation_id "
                    + f"FROM {database}.{sys_obs_2_entity} o "
                    + f"WHERE {sql_where_inject} "
                    + f"GROUP BY o.observation_id HAVING COUNT(DISTINCT o.entity_type) = :entity_types_cardinality"
                    + Param({"entity_types_cardinality": len(distinct_entity_types)})
            )

            records = await self.adapter.exec(sql)

            observation_ids = [record['observation_id'] for record in records.list()]

        stats.hyper_edge_search = hyper_edge_timer.elapsed

        if not observation_ids:
            # No observations in the same context.
            return GraphResponse(
                status=GraphResponseStatusEnum.NOT_FOUND,
                reason=f"I can not recall this. I have not found {' AND '.join(distinct_entity_types)} in one observation.",
                observations=[],
                facts=[],
                stats=stats
            )

        # Conscious Facts
        with timer() as conscious_facts_timer:
            involved_entities = all_entities(entities_in_context)
            if len(involved_entities) == 1:
                sql = (
                        Sql(f"SELECT * ")
                        + f"FROM {database}.sys_v_evt_ent"
                        + "WHERE obs_id in :observation_ids"
                        + "AND (actor_pk IN :entity_pks OR object_pk IN :entity_pks)"
                        + "ORDER BY metadata_time_create ASC"
                        + Param({"observation_ids": observation_ids, "entity_pks": involved_entities})
                )
            else:
                sql = (
                        Sql(f"SELECT * ")
                        + f"FROM {database}.sys_v_evt_ent"
                        + "WHERE obs_id in :observation_ids"
                        + "AND actor_pk IN :entity_pks AND object_pk IN :entity_pks"
                        + "ORDER BY metadata_time_create ASC"
                        + Param({"observation_ids": observation_ids, "entity_pks": involved_entities})
                )

            records = await self.adapter.exec(sql)

        facts = _structure_facts(records)

        stats.fact_search = conscious_facts_timer.elapsed

        if not facts:
            with timer() as observations_timer:
                # Observations
                sql = (
                        Sql(f"SELECT * FROM {database}.sys_v_evt_ent ")
                        + "WHERE obs_id in :observation_ids"
                        + "ORDER BY metadata_time_create ASC"
                        + Param({"observation_ids": observation_ids})
                )

                records = await self.adapter.exec(sql)
                observation_facts = _structure_facts(records)
            stats.context_search = observations_timer.elapsed
        else:
            observation_facts = []

        return GraphResponse(
            status=GraphResponseStatusEnum.OK,
            reason="This is my memory",
            observations=observation_facts,
            facts=facts,
            stats=stats
        )

    async def get_entities_in_hyper_edge(self, entity_pks: List[str], entity_types: List[str] = None):
        if not entity_pks and not entity_types:
            return None

        database = current_bd_database_name()
        sys_obs_2_entity = observation_2_entity_mapping()
        sql = (
                Sql(f"SELECT ")
                + f"observation_id, COUNT(DISTINCT entity_pk) AS matched_entities, GROUP_CONCAT(DISTINCT entity_pk) AS entities"
                + f"FROM {database}.{sys_obs_2_entity}"
                + "WHERE entity_pk in :entity_pks"
                # Adds entity types when there is no property in entity
                + (bool(entity_types), f"OR entity_type in :entity_types", Param({"entity_types": tuple(set(entity_types))}))
                + "GROUP BY observation_id"
                + "ORDER BY matched_entities DESC"
                + Param({"entity_pks": tuple(entity_pks)})
        )

        print(sql.literal())
        return await self.adapter.exec(sql)

    async def get_entities_in_realation_edge(self, entity_pks: List[str], entity_types: List[str] = None):
        database = current_bd_database_name()
        sys_obs_2_entity = observation_2_entity_mapping()
        # sql = (
        #         Sql(f"SELECT ")
        #         + f"observation_id, COUNT(DISTINCT entity_pk) AS matched_entities, GROUP_CONCAT(DISTINCT entity_pk) AS entities"
        #         + f"FROM {database}.{sys_obs_2_entity}"
        #         + "WHERE entity_pk in :entity_pks"
        #         # Adds entity types when there is no property in entity
        #         + (bool(entity_types), f"OR entity_type in :entity_types", Param({"entity_types": tuple(set(entity_types))}))
        #         + "GROUP BY observation_id"
        #         + "ORDER BY matched_entities DESC"
        #         + Param({"entity_pks": tuple(entity_pks)})
        # )
        # return await self.adapter.exec(sql)