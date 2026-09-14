from fastapi import APIRouter, Depends, Response

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.command.event.event import (
    get_event as get_event_cmd,
    delete_event as delete_event_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))]
)


@router.get("/v2/event/{id}", dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            tags=["event"], include_in_schema=sys_config.expose_gui_api)
async def get_event(id: str, response: Response):
    """
    Returns event with given ID
    """
    record = await get_event_cmd(id)

    if record is None:
        response.status_code = 404
        return None

    return {
        "event": record
    }


@router.delete("/v2/event/{id}", tags=["event"],
               dependencies=[Depends(Permissions(roles=["admin", "developer"]))],
               include_in_schema=sys_config.expose_gui_api)
async def delete_event(id: str):
    """
    Deletes event with given ID
    """
    return await delete_event_cmd(id)
