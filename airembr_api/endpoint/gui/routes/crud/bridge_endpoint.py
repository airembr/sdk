from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.command.bridge.bridge import (
    get_data_bridge_by_id as get_data_bridge_by_id_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/bridge/{bridge_id}", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/bridge/{bridge_id}", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
async def get_data_bridge_by_id(bridge_id: str):
    """
    Returns data bridge
    """
    return await get_data_bridge_by_id_cmd(bridge_id)
