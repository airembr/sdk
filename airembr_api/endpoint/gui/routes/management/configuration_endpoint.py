from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from airembr_api.service.grouping import get_grouped_result
from airembr.model.metadata.sys_configuration import Configuration
from airembr.system.adapter.metadata.mysql.mapping.configuration_mapping import map_to_configuration
from airembr.system.command.configuration.errors import ConfigurationError
from airembr.system.command.configuration.configuration import (
    get_configuration as get_configuration_cmd,
    list_defined_configuration as list_defined_configuration_cmd,
    add_configuration as add_configuration_cmd,
    delete_configuration as delete_configuration_cmd,
    list_configuration_types as list_configuration_types_cmd,
)

from airembr_api.endpoint.gui.auth.permissions import Permissions
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


@router.get("/configuration", tags=["configuration"], include_in_schema=sys_config.expose_gui_api)
async def list_defined_configuration(query: Optional[str] = None, limit: int = 200):
    records = await list_defined_configuration_cmd(query, limit)

    return get_grouped_result("Configuration Settings", records, map_to_configuration)


@router.post("/configuration", tags=["configuration"], include_in_schema=sys_config.expose_gui_api)
async def add_configuration(config: Configuration):
    return await add_configuration_cmd(config)


@router.delete("/configuration/{id}", tags=["configuration"], include_in_schema=sys_config.expose_gui_api)
async def delete_configuration(id: str):
    """
    Deletes configuration from the database
    """
    return await delete_configuration_cmd(id)


# Lists

@router.get("/configuration-type", tags=["configuration"], include_in_schema=sys_config.expose_gui_api)
async def list_configuration_types():
    return await list_configuration_types_cmd()
