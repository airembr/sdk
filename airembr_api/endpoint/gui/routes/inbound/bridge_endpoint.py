from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.command.bridge.bridge import (
    reinstall_bridges as reinstall_bridges_cmd,
    get_data_bridges as get_data_bridges_cmd,
    get_data_bridges_meta as get_data_bridges_meta_cmd,
    get_data_bridge_by_id as get_data_bridge_by_id_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/bridge/reinstall", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/bridge/reinstall", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
async def reinstall_bridges():
    await reinstall_bridges_cmd()

@router.get("/v2/bridges", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/bridges", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
async def get_data_bridges():
    """
    Returns list of available data bridges
    """
    return await get_data_bridges_cmd()

@router.get("/v2/bridges/meta", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/bridges/entity", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
async def get_data_bridges_meta():
    """
    Returns list of available data bridges
    """
    return await get_data_bridges_meta_cmd()

@router.get("/v2/bridge/{bridge_id}", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/bridge/{bridge_id}", tags=["bridge"], include_in_schema=sys_config.expose_gui_api)
async def get_data_bridge_by_id(bridge_id: str):
    """
    Returns data bridge
    """
    return await get_data_bridge_by_id_cmd(bridge_id)
