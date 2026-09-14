from typing import Optional

from fastapi import APIRouter, Depends, Response

from airembr_api.endpoint.gui.v1.auth.permissions import Permissions
from airembr.model.metadata.sys_source import EventSource
from airembr.system.config.sys_config import sys_config
from airembr.system.command.event_source.event_source import (
    load_source_by_id as load_source_by_id_cmd,
    save_event_source as save_event_source_cmd,
    delete_event_source as delete_event_source_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/event-source/{id}", tags=["event-source"],
            response_model=Optional[EventSource],
            include_in_schema=sys_config.expose_gui_api)
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
async def save_event_source(source: EventSource):
    """
    Adds new event source in database
    """
    return await save_event_source_cmd(source)


@router.delete("/v2/event-source/{source_id}", tags=["event-source"],
               include_in_schema=sys_config.expose_gui_api)
async def delete_event_source(source_id: str):
    """
    Deletes event source with given ID (str).
    Return False if it is available in draft or production. True if all the instances where deleted
    """

    return await delete_event_source_cmd(source_id)
