from typing import List, Dict, Any, Union

from airembr_api.endpoint.gui.auth.permissions import Permissions
from fastapi import APIRouter, Depends
from airembr.system.config.sys_config import sys_config
from airembr.model.settings import SystemSettings
from airembr.system.command.settings.settings import (
    get_system_settings as get_system_settings_cmd,
    get_system_envs_list as get_system_envs_list_cmd,
    set_cluster_setting as set_cluster_setting_cmd,
    get_cluster_setting as get_cluster_setting_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/system/settings", tags=["system"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=List[SystemSettings])
async def get_system_settings() -> List[SystemSettings]:
    """
    Lists all system settings
    """
    return await get_system_settings_cmd()


@router.get("/system/envs", tags=["system"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=Dict[str, Any])
async def get_system_envs_list() -> Dict[str, Any]:
    """
    Lists all system settings as key value
    """
    return get_system_envs_list_cmd()


@router.put("/cluster/settings/{key}", tags=["system"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=bool)
async def set_cluster_setting(key: str, value: Union[float, bool, str]):
    return await set_cluster_setting_cmd(key, value)


@router.get("/cluster/settings/{key}", tags=["system"],
            include_in_schema=sys_config.expose_gui_api)
async def get_cluster_setting(key: str):
    return await get_cluster_setting_cmd(key)
