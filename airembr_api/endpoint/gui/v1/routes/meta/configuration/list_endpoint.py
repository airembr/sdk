from typing import Optional

from fastapi import APIRouter, Depends

from airembr_api.service.grouping import get_grouped_result
from airembr.system.adapter.metadata.mysql.mapping.configuration_mapping import map_to_configuration
from airembr.system.command.v1.list.configuration.list import (
    list_defined_configuration as list_defined_configuration_cmd,
    list_configuration_types as list_configuration_types_cmd,
)

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "maintainer", "developer"]))]
)


@router.get("/v1/configurations", tags=["v1/configuration"], include_in_schema=sys_config.expose_gui_api)
async def list_defined_configuration(query: Optional[str] = None, limit: int = 200):
    records = await list_defined_configuration_cmd(query, limit)

    return get_grouped_result("Configuration Settings", records, map_to_configuration)


# Lists

@router.get("/v1/configurations/types", tags=["v1/configuration"], include_in_schema=sys_config.expose_gui_api)
async def list_configuration_types():
    return await list_configuration_types_cmd()
