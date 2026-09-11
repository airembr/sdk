from typing import Optional

from fastapi import APIRouter, Depends
from airembr_api.endpoint.gui.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.model.api.request.time_range import DatetimeRangePayload
from airembr.system.command.actor.actor import (
    list_actors as list_actors_cmd,
    get_actors_histogram as get_actors_histogram_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))]
)


@router.post("/v2/actors/list/page/{page}", tags=["v2/data"], include_in_schema=sys_config.expose_gui_api)
@router.post("/v2/actors/list", tags=["v2/data"], include_in_schema=sys_config.expose_gui_api)
async def event_entities(query: DatetimeRangePayload, page: Optional[int] = None):
    return await list_actors_cmd(query, page)


@router.post("/v2/actors/histogram", tags=["v2/data"], include_in_schema=sys_config.expose_gui_api)
async def event_entities_histogram(query: DatetimeRangePayload):
    return await get_actors_histogram_cmd(query)
