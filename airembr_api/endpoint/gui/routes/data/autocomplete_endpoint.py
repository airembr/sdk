from fastapi import APIRouter, Depends
from typing import Optional

from airembr_api.endpoint.gui.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.command.autocomplete.autocomplete import (
    autocomplete_observation as autocomplete_observation_cmd,
    autocomplete_fact as autocomplete_fact_cmd,
    autocomplete_entity_history as autocomplete_entity_history_cmd,
    autocomplete_log as autocomplete_log_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))]
)

@router.get("/v2/observation/query/autocomplete", tags=["v2/autocomplete"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/event/query/autocomplete", tags=["autocomplete"], include_in_schema=sys_config.expose_gui_api)
async def autocomplete_observation_query(query: Optional[str] = ""):
    return await autocomplete_observation_cmd(query)

@router.get("/v2/event/query/autocomplete", tags=["v2/autocomplete"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/event/query/autocomplete", tags=["autocomplete"], include_in_schema=sys_config.expose_gui_api)
async def autocomplete_fact_query(query: Optional[str] = ""):
    return await autocomplete_fact_cmd(query)


@router.get("/v2/actor/query/autocomplete", tags=["v2/autocomplete"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/event/entity/query/autocomplete", tags=["autocomplete"], include_in_schema=sys_config.expose_gui_api)
async def autocomplete_kql(query: Optional[str] = ""):
    return await autocomplete_entity_history_cmd(query)


@router.get("/v2/log/query/autocomplete", tags=["v2/autocomplete"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/log/query/autocomplete", tags=["autocomplete"], include_in_schema=sys_config.expose_gui_api)
async def autocomplete_log_query(query: Optional[str] = ""):
    return await autocomplete_log_cmd(query)
