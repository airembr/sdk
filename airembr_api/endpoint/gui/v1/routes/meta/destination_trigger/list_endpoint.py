from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.v1.list.destination.list import (
    get_destination_triggers_metadata as get_destination_triggers_metadata_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v1/destination-triggers/meta", tags=["v1/destination-triggers"], response_model=dict,
            include_in_schema=sys_config.expose_gui_api)
def list_destination_triggers_metadata() -> dict:
    return get_destination_triggers_metadata_cmd()
