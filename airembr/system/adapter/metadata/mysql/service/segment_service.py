from typing import Tuple, Optional

from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from airembr.system.adapter.metadata.mysql.mapping.sys_ent_segment_mapping import map_to_segment_table, \
    map_to_segment
from airembr.system.adapter.metadata.mysql.schema.table import SysEntSegmentTable
from airembr.model.metadata.sys_ent_segment import EntitySegment


class SegmentService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(SysEntSegmentTable, search, limit, offset)

    async def load_by_id(self, segment_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(SysEntSegmentTable, primary_id=segment_id)

    async def delete_by_id(self, segment_id: str) -> Tuple[bool, Optional[EntitySegment]]:
        return await self.proxy.delete_by_id_in_deployment_mode(SysEntSegmentTable, map_to_segment,
                                                                primary_id=segment_id)

    async def insert(self, segment: EntitySegment):
        return await self.proxy.replace(SysEntSegmentTable, map_to_segment_table(segment))
