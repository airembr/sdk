from typing import Union

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from fastapi import APIRouter, Depends
from airembr.system.config.sys_config import sys_config
from airembr.system.command.settings.settings import (
    set_cluster_setting as set_cluster_setting_cmd,
    get_cluster_setting as get_cluster_setting_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.put("/v1/system/cluster-settings/{key}", tags=["v1/cluster-settings"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=bool)
async def set_cluster_setting(key: str, value: Union[float, bool, str]):
    return await set_cluster_setting_cmd(key, value)


@router.get("/v1/system/cluster-settings/{key}", tags=["v1/cluster-settings"],
            include_in_schema=sys_config.expose_gui_api)
async def get_cluster_setting(key: str):
    return await get_cluster_setting_cmd(key)
