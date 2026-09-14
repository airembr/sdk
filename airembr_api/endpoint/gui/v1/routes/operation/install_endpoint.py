from typing import Optional
from fastapi import APIRouter, HTTPException,Response

from airembr.system.process.installation.installation_status import SystemInstallationStatus
from airembr.system.config.sys_config import sys_config
from airembr.model.system.installer.credentials import Credentials
from airembr.system.command.install.install import (
    check_if_installation_complete as check_if_installation_complete_cmd,
    install as install_cmd,
)
from airembr.system.command.v1.list.bridge.list import (
    reinstall_bridges as reinstall_bridges_cmd
)

from airembr.system.command.tenant.errors import TenantInstallError
from airembr.system.command.tenant.tenant_install import install_tenant as install_tenant_cmd
from airembr.model.system.tenant import TenantCredentials

router = APIRouter()


@router.get("/v1/system/installation/status", tags=["v1/installation"], include_in_schema=sys_config.expose_gui_api, response_model=SystemInstallationStatus)
async def system_installation_status():
    return await check_if_installation_complete_cmd()


@router.post("/v1/system/installation", tags=["v1/installation"], include_in_schema=sys_config.expose_gui_api)
async def system_installation(credentials: Optional[Credentials]):
    try:
        return await install_cmd(credentials)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/v1/bridge/installation", tags=["v1/installation"], include_in_schema=sys_config.expose_gui_api)
async def data_bridges_reinstallation():
    await reinstall_bridges_cmd()


@router.post("/v1/tenant/installation", tags=["v1/installation"], include_in_schema=sys_config.expose_gui_api)
async def install(tenant_creds: TenantCredentials, response: Response):
    try:
        status_code, result = await install_tenant_cmd(tenant_creds)
    except TenantInstallError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    response.status_code = status_code
    return result