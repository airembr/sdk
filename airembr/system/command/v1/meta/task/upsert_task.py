from airembr.model.metadata.sys_task import Task
from airembr.system.adapter.metadata.mysql.service.task_service import BackgroundTaskService

bts = BackgroundTaskService()


async def upsert_task(task: Task):
    return await bts.insert(task)
