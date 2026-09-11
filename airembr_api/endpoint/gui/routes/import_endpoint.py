from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.task.get_task_status import get_task_status as get_task_status_cmd

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)

# TODO Not used probably
@router.get("/import/task/{task_id}/status", tags=["import"], include_in_schema=sys_config.expose_gui_api)
async def get_status(task_id):
    """
    Takes worker task id and returns current status
    """

    return await get_task_status_cmd(task_id)
