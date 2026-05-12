from collections import defaultdict
from typing import Tuple, Dict, Optional, List

from airembr.model.bigdata.flat_fact import FlatFact
from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping


class BdSemanticAdapter(AdapterRouter):

    async def load_stats_of_entity(self, entity_type) -> dict:
        sys_evt = event_mapping()

        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT "
                + f"COUNT(DISTINCT {sys_evt | FlatFact.SOURCE_ID}) as source_ids, "
                + f"COUNT(DISTINCT {sys_evt | FlatFact.ACTOR_ID}) as actor_instances,"
                + f"MIN({sys_evt | FlatFact.METADATA_TIME_INSERT}) as start, "
                + f"MAX({sys_evt | FlatFact.METADATA_TIME_INSERT}) as end, "
                + f"count(DISTINCT {sys_evt | FlatFact.REL_LABEL}) as observation_types, "
                + f"count(DISTINCT {sys_evt | FlatFact.ID}) as observation_instances,  "
                + f"count(DISTINCT {sys_evt | FlatFact.REL_TYPE}) as event_types"
                + f"FROM {database}.{sys_evt}"
                + f"WHERE {sys_evt | FlatFact.ACTOR_TYPE} = :entity_type" + Param({"entity_type": entity_type})
        )

        result = await self.adapter.exec(sql)
        actor_row = result.first()

        sql = (
                Sql()
                + f"SELECT "
                + f"COUNT(DISTINCT {sys_evt | FlatFact.SOURCE_ID}) as source_ids, "
                + f"COUNT(DISTINCT {sys_evt | FlatFact.ACTOR_ID}) as actor_instances,"
                + f"MIN({sys_evt | FlatFact.METADATA_TIME_INSERT}) as start, "
                + f"MAX({sys_evt | FlatFact.METADATA_TIME_INSERT}) as end, "
                + f"count(DISTINCT {sys_evt | FlatFact.REL_LABEL}) as observation_types, "
                + f"count(DISTINCT {sys_evt | FlatFact.ID}) as observation_instances,  "
                + f"count(DISTINCT {sys_evt | FlatFact.REL_TYPE}) as event_types"
                + f"FROM {database}.{sys_evt}"
                + f"WHERE {sys_evt | FlatFact.OBJECT_TYPE} = :entity_type" + Param({"entity_type": entity_type})
        )

        result = await self.adapter.exec(sql)
        object_row = result.first()

        return {
            "actor": {
                "instances": actor_row[1],
                "sources": actor_row[0],
                "start": actor_row[2],
                "end": actor_row[3],
                "observation_types": actor_row[4],
                "observation_instances": actor_row[5],
                "event_types": actor_row[6],
            },
            "object": {
                "instances": object_row[1],
                "sources": object_row[0],
                "start": object_row[2],
                "end": object_row[3],
                "observation_types": object_row[4],
                "observation_instances": object_row[5],
                "event_types": object_row[6],
            }
        }

    async def load_stats_of_entity_events(self, entity_type) -> Dict[str, List[Tuple[str, int]]]:
        sys_evt = event_mapping()

        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT COUNT({sys_evt | FlatFact.REL_LABEL}) as evt_count,"
                  f"{sys_evt | FlatFact.REL_LABEL} as event_type, \"actor\" as entity_type"
                + f"FROM {database}.{sys_evt}"
                + f"WHERE {sys_evt | FlatFact.ACTOR_TYPE} = :entity_type" + Param({"entity_type": entity_type})
                + f"GROUP BY event_type"
                + "UNION"
                + f"SELECT COUNT({sys_evt | FlatFact.REL_LABEL}) as evt_count,"
                  f"{sys_evt | FlatFact.REL_LABEL} as event_type , \"object\" as entity_type"
                + f"FROM {database}.{sys_evt}"
                + f"WHERE {sys_evt | FlatFact.OBJECT_TYPE} = :entity_type" + Param({"entity_type": entity_type})
                + f"GROUP BY event_type"
        )

        result = await self.adapter.exec(sql)

        output = defaultdict(list)
        for row in result:
            output[row['entity_type']].append((row['event_type'], row['evt_count']))
        return output

    async def load_event_types(self, entity_type: Optional[str] = None):

        if entity_type is not None:
            entity_type = entity_type.lower()

        sys_evt = event_mapping()
        database = current_bd_database_name()

        sql = (
                Sql()
                + f"SELECT DISTINCT {sys_evt | FlatFact.REL_LABEL} AS event_type"
                + f"FROM {database}.{sys_evt}"
                + (bool(entity_type),
                   f"WHERE {sys_evt | FlatFact.ACTOR_TYPE}=:entity_type OR {sys_evt | FlatFact.OBJECT_TYPE}=:entity_type ",
                   Param({"entity_type": entity_type}))

        )

        result = await self.adapter.exec(sql)
        for row in result:
            yield row['event_type']

