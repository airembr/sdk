from typing import Optional

from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.command.v1.list.source.list import (
    get_event_source_entities as get_event_source_entities_cmd,
    list_event_sources as list_event_sources_cmd,
    list_running_event_sources as list_running_event_sources_cmd,
    get_event_source_types as get_event_source_types_cmd
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v1/sources",
            tags=["v1/source"],
            include_in_schema=sys_config.expose_gui_api)
async def list_sources(query: Optional[str] = None, output: str = 'entity', limit: int = 100):
    """
    Lists all sources that match given query (str) parameter
    """

    if output == 'meta':
        entities, count = await get_event_source_entities_cmd(query)
        return {
            "total": count,
            "result": entities
        }

    records, count = await list_event_sources_cmd(query, limit)

    return {
        "total": count,
        "grouped": {
            "Sources": records
        },
        "cache": memory_cache_config.source_ttl
    }


@router.get("/v1/sources/running",
            tags=["v1/source"],
            include_in_schema=sys_config.expose_gui_api)
async def list_running_sources(limit: int = 100):
    """
    Lists all sources that match given query (str) parameter
    """

    records, count = await list_running_event_sources_cmd(limit)

    return {
        "total": count,
        "grouped": {
            "Sources": records
        }
    }


@router.get("/v1/sources/types",
            tags=["v1/source"],
            response_model=dict,
            include_in_schema=sys_config.expose_gui_api)
async def list_sources_types() -> dict:
    """
    Returns a list of source types.
    """
    types, count = get_event_source_types_cmd()

    return {
        "total": count,
        "result": types
    }


# @router.get("/v2/event-sources/entity",
#             tags=["v2/source"],
#             include_in_schema=sys_config.expose_gui_api)
# async def list_event_sources_names_and_ids(type: Optional[str] = None):
#     """
#     Returns list of event sources. This list contains only id and name.
#     """
#
#     entities, count = await list_event_sources_names_and_ids_cmd(type)
#     return {
#         "total": count,
#         "result": entities
#     }
