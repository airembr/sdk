from airembr.system.adapter.metadata.mysql.mapping.task_mapping import map_to_task
from airembr.system.adapter.metadata.mysql.service.task_service import BackgroundTaskService

bts = BackgroundTaskService()


async def get_task_status(task_id: str) -> dict:
    record = await bts.load_by_id(task_id)

    if not record.exists():
        return {
            "id": task_id,
            "status": "none",
            "progress": 0,
            "message": None
        }

    task = record.map_to_object(map_to_task)
    return {
        "id": task.id,
        "status": task.status,
        "progress": task.progress,
        "message": task.message
    }
