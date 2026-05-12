from contextlib import asynccontextmanager

from sqlalchemy import desc
from uuid import uuid4

from typing import Optional, Tuple

from airembr.system.logging.log_handler import get_logger
from airembr.model.metadata.sys_task import Task
from airembr.system.adapter.metadata.mysql.mapping.task_mapping import map_to_task_table, map_to_task
from airembr.system.adapter.metadata.mysql.schema.table import TaskTable
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from airembr.sdk.storage.metadata.query.table_filtering import where_tenant_and_mode_context
from airembr.sdk.common.date import now_in_utc

logger = get_logger(__name__)


class BackgroundTaskService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_not_in_deployment_mode(TaskTable,
                                                                search,
                                                                limit,
                                                                offset,
                                                                order_by=desc(TaskTable.timestamp))

    async def load_by_id(self, background_task_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(TaskTable, primary_id=background_task_id)

    async def delete_by_id(self, background_task_id: str) -> Tuple[bool, Optional[Task]]:
        return await self.proxy.delete_by_id_in_deployment_mode(TaskTable, map_to_task,
                                                                primary_id=background_task_id)

    async def update_by_id(self, background_task_id: str, data: dict) -> str:
        return await self.proxy.update_by_id(TaskTable, background_task_id, data)

    async def insert(self, background_task: Task):
        return await self.proxy.replace(TaskTable, map_to_task_table(background_task))

    async def load_all_by_type(self, wf_type: str, search: str = None, columns=None, limit: int = None,
                               offset: int = None) -> SelectResult:
        if search:
            where = where_tenant_and_mode_context(
                TaskTable,
                TaskTable.type == wf_type,
                TaskTable.name.like(f'%{search}%')
            )
        else:
            where = where_tenant_and_mode_context(
                TaskTable,
                TaskTable.type == wf_type
            )

        return await self.proxy.select_in_deployment_mode(
            TaskTable,
            columns=columns,
            where=where,
            order_by=TaskTable.timestamp.desc(),
            limit=limit,
            offset=offset,
            one_record=False)

    async def task_create(self, type: str, name: str, params=None) -> Optional[str]:

        if params is None:
            params = {}
        try:

            task_id = str(uuid4())
            await self.insert(Task(
                id=task_id,
                name=name,
                timestamp=now_in_utc(),
                status="pending",
                progress=0,
                type=type,
                params=params,
                task_id=task_id
            ))
            logger.debug(msg=f"Successfully added task name \"{name}\"")

            return task_id

        except Exception as e:
            logger.error(msg=f"Could not add task with name \"{name}\" due to an error: {str(e)}")

    async def task_progress(self, task_id: str, progress: int):

        try:

            await self.update_by_id(task_id, {
                "progress": progress,
                "status": "running"
            })

            logger.debug(msg=f"Successfully updated task ID \"{task_id}\"")

            return task_id

        except Exception as e:
            logger.error(msg=f"Could not update task with ID \"{task_id}\" due to an error: {str(e)}")

    async def task_finish(self, task_id: str):
        try:
            from airembr.model.system.context import get_context

            await self.update_by_id(task_id, {
                "progress": 100,
                "status": "finished"
            })

            logger.debug(msg=f"Successfully finished task ID \"{task_id}\"")

            return task_id

        except Exception as e:
            logger.error(msg=f"Could not finish task with ID \"{task_id}\" due to an error: {str(e)}")

    async def task_status(self, task_id: str, status, message: Optional[str] = None):
        try:

            bts = BackgroundTaskService()

            await bts.update_by_id(task_id, {
                "status": status,
                "message": message
            })

            logger.debug(msg=f"Successfully changed status for task ID \"{task_id}\"")

            return task_id

        except Exception as e:
            logger.error(msg=f"Could not change status for task with ID \"{task_id}\" due to an error: {str(e)}")


@asynccontextmanager
async def background_log(type: str, name: str):
    bts = BackgroundTaskService()
    task_id = await bts.task_create(type, name)
    try:
        yield bts, task_id
    except Exception as e:
        logger.error(msg=f"Error in background task \"{name}\". Error: {str(e)}")
        await bts.task_status(task_id, "error", str(e))
    finally:
        await bts.task_finish(task_id)
