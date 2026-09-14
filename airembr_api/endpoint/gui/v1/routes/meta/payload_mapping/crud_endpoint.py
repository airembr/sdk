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
)


@router.post("/v1/payload-mapping", tags=["v1/payload-mapping"], include_in_schema=sys_config.expose_gui_api)
async def save_payload_mapping(event_mapping: EventTypeMetadata):
    return await add_event_type_mapping_cmd(event_mapping)


@router.get("/v1/payload-mapping/{event_type_id}",
               tags=["v1/payload-mapping"],
               include_in_schema=sys_config.expose_gui_api,
               response_model=Optional[EventTypeMetadata])
async def get_payload_mapping_by_id(event_type_id: str):
    try:
        return await get_event_mapping_by_id_cmd(event_type_id)
    except EventMappingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.delete("/v1/payload-mapping/{event_type_id}", tags=["v1/payload-mapping"], include_in_schema=sys_config.expose_gui_api)
async def delete_payload_mapping_by_id(event_type_id: str):
    return await del_event_type_metadata_cmd(event_type_id)
