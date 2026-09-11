from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from airembr_api.endpoint.gui.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.model.metadata.sys_event_mapping import EventTypeMetadata
from airembr.system.command.event_mapping.errors import EventMappingError
from airembr.system.command.event_mapping.event_mapping import (
    add_event_type_mapping as add_event_type_mapping_cmd,
    list_event_mappings as list_event_mappings_cmd,
    get_event_mapping_by_id as get_event_mapping_by_id_cmd,
    del_event_type_metadata as del_event_type_metadata_cmd,
    list_event_type_mappings_by_tag as list_event_type_mappings_by_tag_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))],
    prefix="/event-type"
)


@router.post("/mapping", tags=["event-type"], include_in_schema=sys_config.expose_gui_api)
async def add_event_type_mapping(event_mapping: EventTypeMetadata):
    """
    Creates new event type mapping in database
    """
    return await add_event_type_mapping_cmd(event_mapping)


@router.get("/mappings/{event_type}",
            tags=["event-type"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=dict)
async def list_event_mappings(event_type: str):
    """
    Returns a list of event type mappings both build-in and custom for given event type
    """
    try:
        mappings = await list_event_mappings_cmd(event_type)
    except EventMappingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    return {
        "total": len(mappings),
        "result": mappings
    }


@router.get("/mapping/{event_type_id}",
            tags=["event-type"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=Optional[EventTypeMetadata])
async def get_event_mapping_by_id(event_type_id: str):
    """
    Return custom event type mapping for given event type
    """
    try:
        return await get_event_mapping_by_id_cmd(event_type_id)
    except EventMappingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.delete("/mapping/{event_type_id}", tags=["event-type"], include_in_schema=sys_config.expose_gui_api)
async def del_event_type_metadata(event_type_id: str):
    """
    Deletes event type metadata for given event type
    """

    return await del_event_type_metadata_cmd(event_type_id)


@router.get("/search/mappings", tags=["event-type"], include_in_schema=sys_config.expose_gui_api,
            response_model=dict)
async def list_event_type_mappings_by_tag(query: str = None, start: Optional[int] = None, limit: Optional[int] = 200):
    """
    Lists event type metadata by tag, according to given start (int), limit (int) and query (str)
    """

    records, total = await list_event_type_mappings_by_tag_cmd(query, start, limit)

    return {
        "total": total,
        "grouped": {
            "Event mappings": records
        },
        "cache": memory_cache_config.event_mapping_cache_ttl
    }
