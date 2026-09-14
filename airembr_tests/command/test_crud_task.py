import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_task import Task
from airembr.system.adapter.metadata.mysql.service.task_service import BackgroundTaskService
from airembr.system.command.v1.meta.task.upsert_task import upsert_task
from airembr.system.command.v1.meta.task.delete_task import delete_task


def _make_task(task_id: str, status: str = "pending") -> Task:
    return Task(id=task_id, name="Test Task", task_id=task_id, type="import", status=status)


def test_upsert_task_creates_and_updates():
    with ServerContext(Context()):
        async def scenario():
            task_id = f"test-task-{uuid4()}"
            await upsert_task(_make_task(task_id, status="pending"))

            created = await BackgroundTaskService().load_by_id(task_id)
            assert created.map_to_object(lambda row: row).status == "pending"

            await upsert_task(_make_task(task_id, status="finished"))

            updated = await BackgroundTaskService().load_by_id(task_id)
            assert updated.map_to_object(lambda row: row).status == "finished"
        asyncio.run(scenario())


def test_delete_task():
    with ServerContext(Context()):
        async def scenario():
            task_id = f"test-task-{uuid4()}"
            await upsert_task(_make_task(task_id))

            deleted, _record = await delete_task(task_id)

            assert deleted is True
            assert (await BackgroundTaskService().load_by_id(task_id)).map_to_object(lambda row: row) is None
        asyncio.run(scenario())
