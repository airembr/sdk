from fastapi import APIRouter, Depends

from airembr.system.config.sys_config import sys_config
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.command.debug.debug import (
    get_elastic_indices as get_elastic_indices_cmd,
    get_server_time as get_server_time_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin"]))]
)


@router.get("/debug/es/indices", tags=["debug"], include_in_schema=sys_config.expose_gui_api, response_model=dict)
async def get_elastic_indices():
    """
    Returns list of Elasticsearch indices
    """
    return await get_elastic_indices_cmd()


@router.get("/debug/server/time", tags=["debug"], include_in_schema=sys_config.expose_gui_api)
async def get_server_time():
    """
    Returns current server time.
    """

    return await get_server_time_cmd()
