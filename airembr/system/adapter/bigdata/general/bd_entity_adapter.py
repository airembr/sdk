from typing import Optional, List, AsyncGenerator

from durable_dot_dict.collection import DotDictStream
from durable_dot_dict.dotdict import DotDict

from srd.domain.sql import Sql, Param

from airembr.core.json.loader import try_json
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.utils.mapping import get_entity_mapping, entity_history_mapping, sys_ent_2_obs
from airembr.model.bigdata.flat_ent import FlatEntity
from airembr.model.bigdata.flat_ent_history import FlatEntityHistory


class BdEntityAdapter(AdapterRouter):

    # CRUD

    async def load_all_entities(self, entity_type: str, page: int) -> DotDictStream:
        sys_ent = await get_entity_mapping(entity_type)

        if not sys_ent:
            return DotDictStream([])

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT * FROM {database}.{sys_ent} "
                + f"LIMIT :offset, :limit" + Param({"offset": page * 30, "limit": 30})
        )

        records = await self.adapter.exec(sql)

        return records.list()

    async def load_entity_by_hash(self, entity_type: str, hash: str) -> Optional[DotDict]:
        ent = await get_entity_mapping(entity_type)

        if not ent:
            return None

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT * FROM {database}.{ent} "
                + f"WHERE {ent | FlatEntity.HASH} = :hash " + Param({"hash": hash})
        )

        records = await self.adapter.exec(sql)

        return (records >> ent).first()

    async def load_event_entity_by_data_hash_and_ent_pk(self, entity_pk: str, data_hash: str) -> DotDictStream:
        sys_ent_history = entity_history_mapping()

        if not sys_ent_history:
            return DotDictStream([])

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT * "
                + f"FROM {database}.{sys_ent_history} "
                + f"WHERE {sys_ent_history | FlatEntityHistory.DATA_HASH}=:data_hash "
                  f"AND {sys_ent_history | FlatEntityHistory.ENTITY_PK} =:entity_pk "
                + Param({"entity_pk": entity_pk, "data_hash": data_hash})
        )

        records = await self.adapter.exec(sql)
        return (records >> sys_ent_history).first()

    async def count(self, entity_name: str) -> int:
        mapping = await get_entity_mapping(entity_name)

        if not mapping:
            return 0

        records = await self.adapter._count(mapping.table)

        return records.first()[0]

    async def load_entity_by_id(self, entity_id: str) -> DotDict:
        sys_ent_history = entity_history_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT * "
                + f"FROM {database}.{sys_ent_history} "
                + f"WHERE {sys_ent_history | FlatEntityHistory.ENTITY_ID} =:entity_id "
                + Param({"entity_id": entity_id})
        )

        records = await self.adapter.exec(sql)
        return (records >> sys_ent_history).first()

    async def load_entity1_types(self) -> List[str]:
        sys_ent_history = entity_history_mapping()

        if not sys_ent_history:
            return []

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT DISTINCT {sys_ent_history | FlatEntityHistory.ENTITY_TYPE} as entity_type "
                + f"FROM {database}.{sys_ent_history} "
                + "ORDER BY entity_type"
        )

        records = await self.adapter.exec(sql)

        # For some reason it does not return unique entity_types. This may be the DB error

        return list({item['entity_type'] for item in records})

    async def load_observation_entities_for_observer(self, observation_id: str, observer_pk: str) -> AsyncGenerator[DotDict, None]:
        sys_ent_2_obs_map = sys_ent_2_obs()
        sys_sys_ent_history_map = entity_history_mapping()

        if not observation_id:
            return

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT e2o.entity_pk, e2o.entity_type, eh.entity_classification, eh.entity_label, eh.entity_traits, rel_type, rel_label"
                + f"FROM {database}.{sys_ent_2_obs_map} As e2o"
                + f"JOIN {database}.{sys_sys_ent_history_map} AS eh ON e2o.entity_pk = eh.entity_pk"
                + f"WHERE e2o.observation_id = :observation_id AND eh.observer_pk = :observer_pk"
                + Param({"observation_id": observation_id, "observer_pk": observer_pk})
                + "ORDER BY e2o.entity_type"
        )

        result = await self.adapter.exec(sql)
        result = result >> {
                "entity.pk": "entity_pk",
                "entity.type": "entity_type",
                "entity.classification": "entity_classification",
                "entity.label": "entity_label",
                "entity.traits": "entity_traits",
            }
        for item in result:
            traits = item.get('entity.traits', None)
            if traits:
                item['entity.traits'] = try_json(traits)
            yield item


    async def load_observation_entities(self, observation_id: str) -> AsyncGenerator[DotDict, None]:
        sys_ent_2_obs_map = sys_ent_2_obs()
        sys_sys_ent_history_map = entity_history_mapping()

        if not observation_id:
            return

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT e2o.entity_pk, e2o.entity_type, eh.entity_classification, eh.entity_label, eh.entity_traits, rel_type, rel_label"
                + f"FROM {database}.{sys_ent_2_obs_map} As e2o"
                + f"JOIN {database}.{sys_sys_ent_history_map} AS eh ON e2o.entity_pk = eh.entity_pk"
                + f"WHERE e2o.observation_id = :observation_id"
                + Param({"observation_id": observation_id})
                + "ORDER BY e2o.entity_type"
        )

        result = await self.adapter.exec(sql)
        result = result >> {
                "entity.pk": "entity_pk",
                "entity.type": "entity_type",
                "entity.classification": "entity_classification",
                "entity.label": "entity_label",
                "entity.traits": "entity_traits",
            }
        for item in result:
            traits = item.get('entity.traits', None)
            if traits:
                item['entity.traits'] = try_json(traits)
            yield item