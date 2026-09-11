from fastapi import APIRouter, Depends

from airembr.system.adapter.metadata.mysql.mapping.task_mapping import map_to_task
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_task import Task
from airembr_api.service.grouping import get_grouped_result
from airembr.system.command.task.list_tasks import list_tasks as list_tasks_cmd
from airembr.system.command.task.list_tasks_by_type import list_tasks_by_type as list_tasks_by_type_cmd
from airembr.system.command.task.delete_task import delete_task as delete_task_cmd
from airembr.system.command.task.upsert_task import upsert_task as upsert_task_cmd
from airembr.system.command.task.get_task_status import get_task_status as get_task_status_cmd

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/tasks", tags=["task"], include_in_schema=sys_config.expose_gui_api)
async def load_tasks(query: str = None, start: int = 0, limit: int = 100):
    records = await list_tasks_cmd(query, start, limit)
    return get_grouped_result("Tasks", records, map_to_task)


@router.get("/v2/tasks/type/{type}", tags=["task"], include_in_schema=sys_config.expose_gui_api)
async def load_tasks_by_type(type: str, query: str = None, start: int = 0, limit: int = 100):
    """Returns tasks of a given type"""

    records = await list_tasks_by_type_cmd(type, query, start, limit)
    return get_grouped_result("Tasks", records, map_to_task)


@router.delete("/v2/task/{id}", tags=["task"], include_in_schema=sys_config.expose_gui_api)
async def delete_task(id: str):
    return await delete_task_cmd(id)


@router.post("/v2/task", tags=["task"], include_in_schema=sys_config.expose_gui_api)
async def upsert_task(task: Task):
    return await upsert_task_cmd(task)


@router.get("/v2/task/{task_id}/status", tags=["task"], include_in_schema=sys_config.expose_gui_api)
async def get_status(task_id):
    """
    Takes worker task id and returns current status
    """

    return await get_task_status_cmd(task_id)
