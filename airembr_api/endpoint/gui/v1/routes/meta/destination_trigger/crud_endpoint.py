from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.model.destination_trigger import DestinationTrigger
from airembr.system.config.sys_config import sys_config
from airembr.system.command.v1.meta.destination.destination import (
    get_destination_trigger_by_id as get_destination_trigger_by_id_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/destination-trigger/{trigger_id}", tags=["v1/destination-triggers"], response_model=DestinationTrigger,
            include_in_schema=sys_config.expose_gui_api)
def get_destination_trigger_by_id(trigger_id: str) -> DestinationTrigger | None:
    return get_destination_trigger_by_id_cmd(trigger_id)
