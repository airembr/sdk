from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_event_mapping import EventTypeMetadata
from airembr.system.command.v1.errors.payload_mapping_errors import EventMappingError
from airembr.system.command.v1.meta.payload_mapping.event_mapping import (
    add_event_type_mapping as add_event_type_mapping_cmd,
    get_event_mapping_by_id as get_event_mapping_by_id_cmd,
    del_event_type_metadata as del_event_type_metadata_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))],
    prefix="/event-type"
)

# Unprefixed router for canonical /v1/<domain-object> paths: the router above
# applies its "/event-type" prefix to every route it owns, so a canonical
# /v1/payload-mapping path can't be added as a second decorator on it.
router_v1 = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))],
)


@router_v1.post("/v1/payload-mapping", tags=["event-type"], include_in_schema=sys_config.expose_gui_api)
async def save_payload_mapping(event_mapping: EventTypeMetadata):
    """
    Creates new event type mapping in database
    """
    return await add_event_type_mapping_cmd(event_mapping)


@router_v1.get("/v1/payload-mapping/{event_type_id}",
               tags=["event-type"],
               include_in_schema=sys_config.expose_gui_api,
               response_model=Optional[EventTypeMetadata])
async def get_payload_mapping_by_id(event_type_id: str):
    """
    Return custom event type mapping for given event type
    """
    try:
        return await get_event_mapping_by_id_cmd(event_type_id)
    except EventMappingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router_v1.delete("/v1/payload-mapping/{event_type_id}", tags=["event-type"], include_in_schema=sys_config.expose_gui_api)
async def delete_payload_mapping_by_id(event_type_id: str):
    """
    Deletes event type metadata for given event type
    """

    return await del_event_type_metadata_cmd(event_type_id)
