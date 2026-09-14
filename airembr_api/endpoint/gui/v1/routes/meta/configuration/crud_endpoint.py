from fastapi import APIRouter, Depends, HTTPException

from airembr.model.metadata.sys_configuration import Configuration
from airembr.system.command.v1.errors.configuration_errors import ConfigurationError
from airembr.system.command.v1.meta.configuration.configuration import (
    get_configuration as get_configuration_cmd,
    add_configuration as add_configuration_cmd,
    delete_configuration as delete_configuration_cmd,
)

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "maintainer", "developer"]))]
)


@router.get("/configuration/{id}", tags=["configuration"], include_in_schema=sys_config.expose_gui_api)
async def get_configuration(id: str):
    try:
        return await get_configuration_cmd(id)
    except ConfigurationError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/configuration", tags=["configuration"], include_in_schema=sys_config.expose_gui_api)
async def add_configuration(config: Configuration):
    return await add_configuration_cmd(config)


@router.delete("/configuration/{id}", tags=["configuration"], include_in_schema=sys_config.expose_gui_api)
async def delete_configuration(id: str):
    """
    Deletes configuration from the database
    """
    return await delete_configuration_cmd(id)
