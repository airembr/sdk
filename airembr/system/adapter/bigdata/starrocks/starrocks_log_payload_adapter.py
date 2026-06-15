from airembr.system.adapter.bigdata.starrocks.starrocks_base_adapter import StarrocksBaseAdapter
from airembr.system.adapter.bigdata.general.utils.mapping import log_payload_mapping


class StarrocksLogPayloadAdapter(StarrocksBaseAdapter):

    async def save_payload(self, rows: list):
        return await self.stream(rows, log_payload_mapping())
