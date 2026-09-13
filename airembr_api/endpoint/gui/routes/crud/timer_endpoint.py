from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.timer.get_timer import get_timer as get_timer_cmd

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/timer/{timer_id}", tags=["timer"], include_in_schema=sys_config.expose_gui_api)
async def load_timer_by_id(timer_id: str):
    return await get_timer_cmd(timer_id)
