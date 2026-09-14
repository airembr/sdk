from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.command.v1.list.bridge.list import (
    get_data_bridges as get_data_bridges_cmd,
    get_data_bridges_meta as get_data_bridges_meta_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v1/bridges", tags=["v1/bridge"], include_in_schema=sys_config.expose_gui_api)
async def get_data_bridges():
    """
    Returns list of available data bridges
    """
    return await get_data_bridges_cmd()

@router.get("/v1/bridges/meta", tags=["v1/bridge"], include_in_schema=sys_config.expose_gui_api)
async def get_data_bridges_meta():
    """
    Returns list of available data bridges
    """
    return await get_data_bridges_meta_cmd()
