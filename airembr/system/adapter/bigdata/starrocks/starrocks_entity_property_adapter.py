import asyncio
import hashlib
from datetime import datetime
from typing import Optional, Tuple, List, Dict, AsyncGenerator

from durable_dot_dict.dotdict import DotDict

from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.general.bd_entity_history_adapter import BdEntityHistoryAdapter
from airembr.system.adapter.bigdata.starrocks.starrocks_eql import (
    build_select_observation_will_all_entities,
    build_select_expanded_entities_from_observations,
    build_select_entity_types_from_observations,
    build_select_observations_with_eql,
    EmbeddingMap,
)
from airembr.system.adapter.bigdata.starrocks.utils.sql_entity_search import sql_entity_by_properties
from airembr.system.adapter.bigdata.starrocks.utils.sql_text import (
    count_not_embedded_property_values_sql,
    load_not_embedded_property_values_sql,
    similar_observations_sql,
)
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.utils.mapping import entity_property
from airembr.model.bigdata.flat_ent_property import FlatEntityProperty
from airembr.sdk.service.remote.embedding_api_client import EmbeddingApiClient
from airembr.sdk.ai.config import embedding_host, embedding_api_key


class StarrocksEntityPropertyAdapter(BdEntityHistoryAdapter):

    @staticmethod
    def _parse_merged_properties(pk, type, properties, fit, count):
        props = properties.split(' <||> ')

        out = {}
        for prop in props:
            if prop.strip() == '':
                continue

            values = prop.split("=", 1)
            if len(values) != 2:
                continue

            key, value = values
            out[key] = value

        return DotDict({"pk": pk, "type": type, "fit": fit / count if count > 0 else None,
                        "traits": (DotDict() << out).to_dict()})

    async def load_entities_with_vectors(self, entity_types: List[str],
                                         observer_pk: Optional[str] = None):
        database = current_bd_database_name()
        sys_ent_property = entity_property()

        sql = (
                Sql()
                + "SELECT *"
                + f"FROM {database}.{sys_ent_property} AS entity"
                + f"WHERE {sys_ent_property | FlatEntityProperty.VECTOR} IS NOT NULL "
                  f"AND {sys_ent_property | FlatEntityProperty.TYPE} IN :entity_types" + Param(
            {"entity_types": tuple(set(entity_types))})
                + (bool(observer_pk), f"AND {sys_ent_property | FlatEntityProperty.OBSERVER_PK} = :observer_pk",
                   Param({"observer_pk": observer_pk}))
                # This limit caused problems - for some reason it was cutting the number of records incorrectly
                # So it was increased
                + f"LIMIT :offset, :limit" + Param({"offset": 0, "limit": 10000})
        )

        result = await self.adapter.exec(sql)
        return result >> sys_ent_property

    async def load_entities_with_property(self,
                                          entity_type: str,
                                          property_name: str, property_value: str,
                                          observer_pk: Optional[str] = None):
        database = current_bd_database_name()
        sys_ent_property = entity_property()

        sql = (
                Sql()
                + "SELECT *"
                + f"FROM {database}.{sys_ent_property} AS entity"
                + f"WHERE {sys_ent_property | FlatEntityProperty.NAME} = :property_name AND {sys_ent_property | FlatEntityProperty.VALUE} = :property_value "
                  f"AND {sys_ent_property | FlatEntityProperty.TYPE} = :entity_type"
                + Param({"property_name": property_name, "property_value": property_value, "entity_type": entity_type})
                + (bool(observer_pk), f"AND {sys_ent_property | FlatEntityProperty.OBSERVER_PK} = :observer_pk",
                   Param({"observer_pk": observer_pk}))
                # This limit caused problems - for some reason it was cutting the number of records incorrectly
                # So it was increased
                + f"LIMIT :offset, :limit" + Param({"offset": 0, "limit": 1000})
        )

        result = await self.adapter.exec(sql)
        return result >> sys_ent_property

    async def load_entity_by_properties(self, query: List[Tuple[str, str]], entity_type: Optional[str] = None,
                                        observer_pk: Optional[str] = None, page: Optional[int] = 0):

        # TODO: This should be replaced either by stitched entities or entities computed by proeprty state.

        database = current_bd_database_name()
        sys_ent_property = entity_property()

        sql = sql_entity_by_properties(query, entity_type, observer_pk)

        sql += (
                Sql()
                # Final aggregation
                + "SELECT entity.entity_pk, entity.entity_type, entity.count,"
                + f"GROUP_CONCAT(CONCAT_WS('=', prop.{sys_ent_property | FlatEntityProperty.NAME}, prop.{sys_ent_property | FlatEntityProperty.VALUE}) ORDER BY prop.ts ASC SEPARATOR ' <||> ') AS properties"
                + "FROM queried_entity_properties AS entity"
                + f"INNER JOIN {database}.{sys_ent_property} AS prop ON entity.entity_pk = prop.entity_pk "
                + (bool(observer_pk), "AND prop.observer_pk = :observer_pk", Param({"observer_pk": observer_pk}))
                + "GROUP BY entity.entity_pk, entity.entity_type, entity.count"
                + "ORDER BY entity.count DESC"
                + f"LIMIT :offset, :limit" + Param({"offset": page * 30, "limit": 30})
        )

        result = await self.adapter.exec(sql)
        # In result properties are concatenated strings of all traits changes. The last one is the most recent.
        return [self._parse_merged_properties(
            item['entity_pk'],
            item['entity_type'],
            item['properties'],
            item['count'],
            len(query)
        ) for item in result]

    async def yield_not_embedded_properties(self):
        sys_ent_property = entity_property()
        database = current_bd_database_name()
        sql = (Sql()
               + f"SELECT * FROM {database}.{sys_ent_property}"
               + f"WHERE {sys_ent_property | FlatEntityProperty.VECTOR} IS NULL"
               )
        result = await self.adapter.exec(sql)
        return result >> sys_ent_property

    async def update_property_embeddings(self, data: Dict[str, List[float]]):

        # TODO slow implementation
        sys_ent_property = entity_property()
        database = current_bd_database_name()

        for id, vector in data.items():
            sql = Sql(f"UPDATE {database}.{sys_ent_property} ")
            sql += f"SET {sys_ent_property | FlatEntityProperty.VECTOR} = {list(vector)} "
            sql += f"WHERE {sys_ent_property | FlatEntityProperty.PROPERTY_ID} = :id"
            sql += Param({"id": id})
            await self.adapter.exec(sql)

    async def _prepare_embeddings(self, entities) -> Optional[EmbeddingMap]:
        """Embed all ~ property values and return an EmbeddingMap for the SQL builder.

        Uses MD5 of the (entity_type, prop_name, value) triple as the string key
        sent to the embedding API, then maps responses back to the original tuples.
        Returns None when embedding is unconfigured or no ~ properties are present.
        """
        if not embedding_host or not embedding_api_key:
            return None

        texts: Dict[str, str] = {}
        key_map: Dict[str, tuple] = {}

        for entity in entities:
            for prop in (entity.properties or []):
                if prop.assign == "~":
                    tup = (entity.type, prop.name, str(prop.value))
                    md5_key = hashlib.md5("|".join(tup).encode()).hexdigest()
                    texts[md5_key] = str(prop.value)
                    key_map[md5_key] = tup

        if not texts:
            return None

        client = EmbeddingApiClient(embedding_host, embedding_api_key)
        emb = await asyncio.to_thread(lambda: client.call(texts).get_mapped_embeddings())
        if not emb or not emb.dense:
            return None

        result: EmbeddingMap = {}
        for md5_key, vector in emb.dense.items():
            tup = key_map.get(md5_key)
            if tup is not None:
                result[tup] = vector
        return result or None

    async def yield_exact_entities_with_eql(self, eql_object, unmatched_entities: int = 0, unmatched_traits: int = 0,
                                            start_date: Optional[datetime] = None,
                                            end_date: Optional[datetime] = None) -> AsyncGenerator[
        Tuple[str, List[str], int], None]:
        embeddings = await self._prepare_embeddings(eql_object)
        sql = build_select_observation_will_all_entities(eql_object,
                                                         unmatched_entities,
                                                         unmatched_traits,
                                                         start_date=start_date,
                                                         end_date=end_date,
                                                         embeddings=embeddings)

        result = await self.adapter.exec(sql)
        if not result:
            return
        for item in result:
            yield item['observation_id'], item['entity_pks'].split(','), int(item['no_of_matched_props'])

    async def load_expanded_entities_with_eql(self, eql_object, entity_types: list, unmatched_entities: int = 0,
                                              unmatched_traits: int = 0,
                                              start_date: Optional[datetime] = None,
                                              end_date: Optional[datetime] = None,
                                              traits_source: str = "ent_state"):
        embeddings = await self._prepare_embeddings(eql_object)
        sql = build_select_expanded_entities_from_observations(
            eql_object,
            entity_types,
            unmatched_entities,
            unmatched_traits,
            start_date=start_date,
            end_date=end_date,
            embeddings=embeddings,
            traits_source=traits_source)
        return await self.adapter.exec(sql)

    async def load_observations_with_eql(self, eql_object, unmatched_entities: int = 0, unmatched_traits: int = 0,
                                         start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        embeddings = await self._prepare_embeddings(eql_object)
        sql = build_select_observations_with_eql(eql_object, unmatched_entities, unmatched_traits,
                                                 start_date=start_date, end_date=end_date, embeddings=embeddings)
        print(1, sql.literal())
        return await self.adapter.exec(sql)

    async def load_entity_types_with_eql(self, eql_object, unmatched_entities: int = 0, unmatched_traits: int = 0,
                                         start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        embeddings = await self._prepare_embeddings(eql_object)
        sql = build_select_entity_types_from_observations(eql_object, unmatched_entities, unmatched_traits,
                                                          start_date=start_date, end_date=end_date,
                                                          embeddings=embeddings)
        return await self.adapter.exec(sql)

    async def count_not_embedded_property_values(self):
        sql = count_not_embedded_property_values_sql()
        result = await self.adapter.exec(sql)
        return result.first().column(0) if result else 0

    async def load_not_embedded_property_values(self):
        sql = load_not_embedded_property_values_sql()
        print(1, sql.literal())
        return await self.adapter.exec(sql)

    async def semantic_search(self, query: str, limit: int = 10) -> None:
        emb_client = EmbeddingApiClient(embedding_host, embedding_api_key)
        response = await asyncio.to_thread(lambda: emb_client.call({"query": query}).get_mapped_embeddings())
        query_vector = response.dense["query"]

        sql = similar_observations_sql(query_vector, limit)
        result = await self.adapter.exec(sql)

        vector_sim_result: List[dict] = {row.get('observation_id', None):dict(row) for row in result} if result else {}
        return vector_sim_result
