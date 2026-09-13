from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_task import Task
from airembr.system.command.task.delete_task import delete_task as delete_task_cmd
from airembr.system.command.task.upsert_task import upsert_task as upsert_task_cmd

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.delete("/v2/task/{id}", tags=["task"], include_in_schema=sys_config.expose_gui_api)
async def delete_task(id: str):
    return await delete_task_cmd(id)


@router.post("/v2/task", tags=["task"], include_in_schema=sys_config.expose_gui_api)
async def upsert_task(task: Task):
    return await upsert_task_cmd(task)
