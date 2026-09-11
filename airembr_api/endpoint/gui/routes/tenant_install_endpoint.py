from fastapi import APIRouter, Response, HTTPException
from airembr.model.system.tenant import TenantCredentials
from airembr.system.config.sys_config import sys_config
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.command.tenant.errors import TenantInstallError
from airembr.system.command.tenant.tenant_install import install_tenant as install_tenant_cmd

logger = get_logger(__name__)

router = APIRouter()


@router.post("/tenant/install", tags=["multi-tenant"], include_in_schema=sys_config.expose_gui_api)
async def install(tenant_creds: TenantCredentials, response: Response):
    try:
        status_code, result = await install_tenant_cmd(tenant_creds)
    except TenantInstallError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    response.status_code = status_code
    return result
