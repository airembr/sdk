from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.command.v1.errors.payload_mapping_errors import EventMappingError
from airembr.system.command.v1.meta.payload_mapping.event_mapping import (
    list_event_mappings as list_event_mappings_cmd,
    list_event_type_mappings_by_tag as list_event_type_mappings_by_tag_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))],
    prefix="/event-type"
)


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
