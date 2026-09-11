from typing import Optional

from airembr.sdk.storage.metadata.query.select_result import SelectResult
from airembr.system.adapter.metadata.mysql.service.task_service import BackgroundTaskService

bts = BackgroundTaskService()


async def list_tasks(query: Optional[str], start: int, limit: int) -> SelectResult:
    return await bts.load_all(search=query, offset=start, limit=limit)
