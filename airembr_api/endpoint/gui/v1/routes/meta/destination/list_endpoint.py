from typing import Optional

from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.command.v1.list.destination.list import (
    get_destinations_type_list as get_destinations_type_list_cmd,
    get_destinations_by_tag as get_destinations_by_tag_cmd,
    get_destinations_meta as get_destinations_meta_cmd
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/destinations/type", tags=["destination"], response_model=dict, include_in_schema=sys_config.expose_gui_api)
async def list_destinations_types():
    """
    Returns destination types.
    """
    return await get_destinations_type_list_cmd()


@router.get("/v1/destinations", tags=["v1/destination"], response_model=dict,
            include_in_schema=sys_config.expose_gui_api)
async def list_destinations(query: Optional[str] = None, start: int = 0, limit: int = 100) -> dict:
    destinations, total = await get_destinations_by_tag_cmd(query, start, limit)

    return {
        "total": total,
        "grouped": {
            "Triggers": destinations
        },
        "cache": memory_cache_config.destination_cache_ttl
    }


@router.get("/v1/destinations/meta", tags=["v1/destination"], response_model=dict,
            include_in_schema=sys_config.expose_gui_api)
async def list_destinations_meta(query: Optional[str] = None, start: int = 0, limit: int = 100) -> dict:
    destinations, total = await get_destinations_meta_cmd(query, start, limit)
    return {
        "total": total,
        "result": destinations
    }