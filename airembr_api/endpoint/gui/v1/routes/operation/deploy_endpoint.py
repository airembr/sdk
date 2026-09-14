from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.deploy.deploy import set_deployment as set_deployment_cmd

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v1/deployment/{table_name}/{id}", tags=["v2/deployment"], include_in_schema=sys_config.expose_gui_api)
async def production_deployment(table_name: str, id: str, action: str):
    return await set_deployment_cmd(table_name, id, action == 'deploy')
