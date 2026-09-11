from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.dashboard.dashboard import (
    count_online_resources as count_online_resources_cmd,
    get_table_stats as get_table_stats_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", 'marketer', "maintainer"]))]
)


# TODO change endpoint to /v2/dashboard
@router.get("/v2/count/online", tags=["v2/dashboard"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def count_online_resources():
    return await count_online_resources_cmd()


# TODO change endpoint to /v2/dashboard
@router.get("/v2/system/table/stats", tags=["v2/dashboard"], include_in_schema=sys_config.expose_gui_api)
async def get_table_stats():
    return await get_table_stats_cmd()
