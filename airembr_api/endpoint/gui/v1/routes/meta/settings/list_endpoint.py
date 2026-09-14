from typing import List

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from fastapi import APIRouter, Depends
from airembr.system.config.sys_config import sys_config
from airembr.model.settings import SystemSettings
from airembr.system.command.settings.settings import (
    get_system_settings as get_system_settings_cmd
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v1/system/settings", tags=["v1/settings"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=List[SystemSettings])
async def list_system_settings() -> List[SystemSettings]:
    """
    Lists all system settings
    """
    return await get_system_settings_cmd()

