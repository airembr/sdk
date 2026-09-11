from typing import Optional

from fastapi import APIRouter
from fastapi import Depends

from airembr.model.api.request.time_range import DatetimeRangePayload
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.log.log_query import (
    load_logs as load_logs_cmd,
    load_log_histogram as load_log_histogram_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))]
)


@router.post("/log/range/page/{page}",
             tags=["log"],
             include_in_schema=sys_config.expose_gui_api)
async def load_logs(query: DatetimeRangePayload, page: Optional[int] = None):
    return await load_logs_cmd(query, page)


@router.post("/log/histogram",
             tags=["log"],
             include_in_schema=sys_config.expose_gui_api)
async def load_log_histogram(query: DatetimeRangePayload, page: Optional[int] = None):
    return await load_log_histogram_cmd(query, page)
