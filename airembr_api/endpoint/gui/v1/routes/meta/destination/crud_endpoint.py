from typing import Optional
from fastapi import APIRouter, Response, Depends
from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

from airembr.model.metadata.sys_destination import Destination
from airembr.system.config.sys_config import sys_config
from airembr.system.command.v1.meta.destination.destination import (
    save_destination as save_destination_cmd,
    get_destination as get_destination_cmd,
    delete_destination_by_id as delete_destination_by_id_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.post("/v1/destination", tags=["destination"], include_in_schema=sys_config.expose_gui_api)
async def save_destination(destination: Destination):
    """
    Upserts destination data.
    """
    await save_destination_cmd(destination)


@router.get("/v1/destination/{destination_id}", tags=["destination"], response_model=Optional[Destination],
            include_in_schema=sys_config.expose_gui_api)
async def get_destination_by_id(destination_id: str, response: Response):
    """
    Returns destination or None if destination does not exist.
    """

    destination = await get_destination_cmd(destination_id)

    if not destination:
        response.status_code = 404
        return None

    return destination


@router.delete("/v1/destination/{destination_id}", tags=["destination"], include_in_schema=sys_config.expose_gui_api)
async def delete_destination_by_id(destination_id: str):
    """
    Deletes destination with given id
    """
    return await delete_destination_by_id_cmd(destination_id)
