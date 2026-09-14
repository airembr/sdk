from typing import Optional, Tuple

from airembr.model.metadata.sys_task import Task
from airembr.system.adapter.metadata.mysql.service.task_service import BackgroundTaskService

bts = BackgroundTaskService()


async def delete_task(task_id: str) -> Tuple[bool, Optional[Task]]:
    return await bts.delete_by_id(task_id)
