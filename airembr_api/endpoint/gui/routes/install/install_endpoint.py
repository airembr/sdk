from typing import Optional
from fastapi import APIRouter, HTTPException

from airembr.system.process.installation.installation_status import SystemInstallationStatus
from airembr.system.config.sys_config import sys_config
from airembr.model.system.installer.credentials import Credentials
from airembr.system.command.install.install import (
    check_if_installation_complete as check_if_installation_complete_cmd,
    install as install_cmd,
)

router = APIRouter()


@router.get("/v2/install", tags=["installation"], include_in_schema=sys_config.expose_gui_api, response_model=SystemInstallationStatus)
async def check_if_installation_complete():
    """
    Returns list of missing and updated indices
    """
    return await check_if_installation_complete_cmd()


@router.post("/v2/install", tags=["installation"], include_in_schema=sys_config.expose_gui_api)
async def install(credentials: Optional[Credentials]):

    try:
        return await install_cmd(credentials)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
