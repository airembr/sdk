from typing import Optional

from fastapi import APIRouter, Depends, Response

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.model.metadata.sys_source import EventSource
from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.command.event_source.event_source import (
    get_event_source_entities as get_event_source_entities_cmd,
    list_event_sources as list_event_sources_cmd,
    list_running_event_sources as list_running_event_sources_cmd,
    get_event_source_types as get_event_source_types_cmd,
    load_source_by_id as load_source_by_id_cmd,
    save_event_source as save_event_source_cmd,
    delete_event_source as delete_event_source_cmd,
    list_event_sources_names_and_ids as list_event_sources_names_and_ids_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/event-sources",
            tags=["event-source"],
            include_in_schema=sys_config.expose_gui_api)
async def list_event_sources(query: str = None, output: str = 'entity', limit: int = 100):
    """
    Lists all event sources that match given query (str) parameter
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


@router.get("/v2/event-sources/running",
            tags=["event-source"],
            include_in_schema=sys_config.expose_gui_api)
# @router.get("/event-sources/running",
#             tags=["event-source"],
#             include_in_schema=sys_config.expose_gui_api)
async def list_running_event_sources(limit: int = 100):
    """
    Lists all event sources that match given query (str) parameter
    """

    records, count = await list_running_event_sources_cmd(limit)

    return {
        "total": count,
        "grouped": {
            "Sources": records
        }
    }


@router.get("/v2/event-sources/type",
            tags=["event-source"],
            response_model=dict,
            include_in_schema=sys_config.expose_gui_api)
async def get_event_source_types() -> dict:
    """
    Returns a list of event source types.
    """
    types, count = get_event_source_types_cmd()

    return {
        "total": count,
        "result": types
    }


@router.get("/v2/event-source/{id}", tags=["event-source"],
            response_model=Optional[EventSource],
            include_in_schema=sys_config.expose_gui_api)
# @router.get("/event-source/{id}", tags=["event-source"],
#             response_model=Optional[EventSource],
#             include_in_schema=sys_config.expose_gui_api)
async def load_source_by_id(id: str, response: Response):
    """
    Returns event source with given ID (str)
    """

    record = await load_source_by_id_cmd(id)

    if not record:
        response.status_code = 404
        return None

    return record


@router.post("/v2/event-source", tags=["event-source"],
             include_in_schema=sys_config.expose_gui_api)
# @router.post("/event-source", tags=["event-source"],
#              include_in_schema=sys_config.expose_gui_api)
async def save_event_source(source: EventSource):
    """
    Adds new event source in database
    """
    return await save_event_source_cmd(source)


@router.delete("/v2/event-source/{source_id}", tags=["event-source"],
               include_in_schema=sys_config.expose_gui_api)
# @router.delete("/event-source/{source_id}", tags=["event-source"],
#                include_in_schema=sys_config.expose_gui_api)
async def delete_event_source(source_id: str):
    """
    Deletes event source with given ID (str).
    Return False if it is available in draft or production. True if all the instances where deleted
    """

    return await delete_event_source_cmd(source_id)


@router.get("/v2/event-sources/entity",
            tags=["event-source"],
            include_in_schema=sys_config.expose_gui_api)
# @router.get("/event-sources/entity",
#             tags=["event-source"],
#             include_in_schema=sys_config.expose_gui_api)
async def list_event_sources_names_and_ids(type: Optional[str] = None):
    """
    Returns list of event sources. This list contains only id and name.
    """

    entities, count = await list_event_sources_names_and_ids_cmd(type)
    return {
        "total": count,
        "result": entities
    }
