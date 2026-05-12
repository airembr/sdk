from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.general.utils.mapping import event_job_mapping


class DbEventJobAdapter(AdapterRouter):

    async def stream(self, rows):
        sys_evt_job = event_job_mapping()
        return await self.adapter.stream(rows, sys_evt_job)
