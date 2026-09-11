from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.deploy.deploy import set_deployment as set_deployment_cmd

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/deploy/{table_name}/{id}", tags=["deployment"], include_in_schema=sys_config.expose_gui_api)
async def deploy_object(table_name: str, id: str):
    return await set_deployment_cmd(table_name, id, True)


@router.get("/undeploy/{table_name}/{id}", tags=["deployment"], include_in_schema=sys_config.expose_gui_api)
async def undeploy_object(table_name: str, id: str):
    return await set_deployment_cmd(table_name, id, False)


@router.get("/v2/production/{table_name}/{id}", tags=["v2/deployment"], include_in_schema=sys_config.expose_gui_api)
async def production_deployment(table_name: str, id: str, action: str):
    return await set_deployment_cmd(table_name, id, action == 'deploy')
