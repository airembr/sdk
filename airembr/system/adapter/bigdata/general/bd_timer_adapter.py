from typing import Optional

from durable_dot_dict.collection import DotDictStream

from srd.domain.result import Row
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter

from srd.domain.sql import Sql, Param
from airembr.system.adapter.bigdata.general.utils.mapping import sys_timer_mapping
from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.model.bigdata.flat_sys_timer import FlatSysTimer


class BdTimerAdapter(AdapterRouter):

    async def load_timer(self, timer_id: str) -> Optional[Row]:
        sys_timer = sys_timer_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT  *"
                + f"FROM {database}.{sys_timer} "
                + f"WHERE {sys_timer | FlatSysTimer.ID} = :timer_id" + Param({"timer_id": timer_id})
        )

        result = await self.adapter.exec(sql)
        if not result:
            return None
        return result.first_as(sys_timer)

    async def load_active_timers(self) -> DotDictStream:
        sys_timer = sys_timer_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"SELECT  *"
                + f"FROM {database}.{sys_timer} "
                + f"WHERE {sys_timer | FlatSysTimer.STATUS} > 0"  # Filter active
                + f"AND DATE_ADD({sys_timer | FlatSysTimer.TS}, INTERVAL {sys_timer | FlatSysTimer.TIMEOUT} SECOND) < now() "
                + f"AND status > 0"
        )

        result = await self.adapter.exec(sql)
        return result >> sys_timer

    async def reset_timers(self):
        sys_timer = sys_timer_mapping()

        database = current_bd_database_name()
        sql = (
                Sql()
                + f"DELETE FROM {database}.{sys_timer} "
                + f"WHERE DATE_ADD({sys_timer | FlatSysTimer.TS}, INTERVAL 7 DAY) < now() "
        )

        await self.adapter.exec(sql)
