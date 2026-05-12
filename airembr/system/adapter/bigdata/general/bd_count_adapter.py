from typing import Tuple

from srd.domain.sql import Sql

from airembr.model.bigdata.flat_fact import FlatFact
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.general.helpers.filters import within
from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name


class BdCountAdapter(AdapterRouter):

    async def count_online_observations(self) -> Tuple[int, int, int, int]:
        sys_evt = event_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT "
                  f" COUNT(DISTINCT {sys_evt | FlatFact.OBS_ID}) as observations_count, "
                  f" COUNT(DISTINCT {sys_evt | FlatFact.ACTOR_ID}) as actors_count, "
                  f" COUNT(DISTINCT {sys_evt | FlatFact.ACTOR_TYPE}) as actors_types"
                + f"FROM {database}.{sys_evt} "
                + f"WHERE {sys_evt | FlatFact.METADATA_TIME_INSERT} > {within('1 HOUR')}"
        )
        result = await self.adapter.exec(sql)
        result = result.first()
        observations_count, actors_count, actor_types = result if result is not None else [0, 0, 0]

        sql = (
                Sql()
                + f"SELECT COUNT(*) as events_count FROM {database}.{sys_evt} "
                + f"WHERE {sys_evt | FlatFact.METADATA_TIME_INSERT} > {within('1 HOUR')} "
        )

        result = await self.adapter.exec(sql)
        result = result.first()
        events_count = result.column(0) if result is not None else 0

        return observations_count, events_count, actor_types, actors_count
