from typing import Optional, List
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.general.sql.pks_stitched_by_iid import sql_pks_stitched_by_iid_for_pk


class BdGid2PKAdapter(AdapterRouter):

    async def load_pks_stitched_by_iid(self, entity_pk: str) -> Optional[List]:
        sql = sql_pks_stitched_by_iid_for_pk(entity_pk)

        result = await self.adapter.exec(sql)

        if not result:
            return None

        return result.list()
