from typing import Dict
from fastapi import APIRouter, Depends
from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.model.metadata.sys_resource import Resource
from airembr.system.config.sys_config import sys_config

from airembr.system.command.v1.list.destination.list import (

    list_destination_resources as list_destination_resources_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v1/destination-resources/meta",
            tags=["v1/destination-resources"],
            response_model=Dict[str, Resource],
            include_in_schema=sys_config.expose_gui_api)
async def list_destination_resources():
    return await list_destination_resources_cmd()
