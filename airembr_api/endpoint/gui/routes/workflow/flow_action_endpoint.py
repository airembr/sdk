from typing import Optional
from fastapi import APIRouter
from fastapi import HTTPException, Depends

from airembr.model.system.enum.yes_no import YesNo

from airembr_api.endpoint.gui.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.command.plugin.errors import PluginError
from airembr.system.command.plugin.plugin import (
    get_plugin as get_plugin_cmd,
    get_plugin_state as get_plugin_state_cmd,
    set_plugin_enabled_disabled as set_plugin_enabled_disabled_cmd,
    edit_plugin_icon as edit_plugin_icon_cmd,
    edit_plugin_name as edit_plugin_name_cmd,
    delete_plugin as delete_plugin_cmd,
    get_plugins_list as get_plugins_list_cmd,
    install_plugins as install_plugins_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/flow/action/plugin/{plugin_id}",
            tags=["flow", "action"],
            include_in_schema=sys_config.expose_gui_api)
async def get_plugin(plugin_id: str):
    """
    Returns FlowActionPlugin object.
    """
    try:
        return await get_plugin_cmd(plugin_id)
    except PluginError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/flow/action/plugin/{plugin_id}/hide/{state}", tags=["flow", "action"],
            include_in_schema=sys_config.expose_gui_api)
async def get_plugin_state(plugin_id: str, state: YesNo):
    """
    Returns FlowActionPlugin object.
    """
    return await get_plugin_state_cmd(plugin_id, state)


@router.get("/flow/action/plugin/{plugin_id}/enable/{state}", tags=["flow", "action"],
            include_in_schema=sys_config.expose_gui_api)
async def set_plugin_enabled_disabled(plugin_id: str, state: YesNo):
    """
    Sets FlowActionPlugin enabled or disabled.
    """
    return await set_plugin_enabled_disabled_cmd(plugin_id, state)


@router.put("/flow/action/plugin/{plugin_id}/icon/{icon}", tags=["flow", "action"],
            include_in_schema=sys_config.expose_gui_api)
async def edit_plugin_icon(plugin_id: str, icon: str):
    """
    Edits icon for action with given ID
    """
    return await edit_plugin_icon_cmd(plugin_id, icon)


@router.put("/flow/action/plugin/{plugin_id}/name/{name}", tags=["flow", "action"],
            include_in_schema=sys_config.expose_gui_api)
async def edit_plugin_name(plugin_id: str, name: str):
    """
    Edits name for action with given ID
    """
    return await edit_plugin_name_cmd(plugin_id, name)


@router.delete("/flow/action/plugin/{plugin_id}", tags=["flow", "action"],
               include_in_schema=sys_config.expose_gui_api)
async def delete_plugin(plugin_id: str):
    """
    Deletes FlowActionPlugin object.
    """
    return await delete_plugin_cmd(plugin_id)


@router.get("/flow/action/plugins", tags=["flow", "action"],
            include_in_schema=sys_config.expose_gui_api)
async def get_plugins_list(flow_type: Optional[str] = None, query: Optional[str] = None):
    """
    Returns a list of available plugins.
    """
    return await get_plugins_list_cmd(flow_type, query)


@router.get("/v2/install/plugins", tags=["installation"], include_in_schema=sys_config.expose_gui_api)
async def install_plugins():
    return await install_plugins_cmd()
