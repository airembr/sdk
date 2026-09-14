from typing import Optional
from fastapi import APIRouter, Depends

from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_resource import Resource
from airembr.system.command.resource.resource import (
    get_resource_by_id as get_resource_by_id_cmd,
    upsert_resource as upsert_resource_cmd,
    delete_resource as delete_resource_cmd,
)
from airembr_api.endpoint.gui.v1.auth.permissions import Permissions

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/resource/{id}",
            tags=["resource"],
            response_model=Optional[Resource],
            include_in_schema=sys_config.expose_gui_api)
async def get_resource_by_id(id: str) -> Optional[Resource]:
    """
    Returns source data with given id.
    """

    return await get_resource_by_id_cmd(id)


@router.post("/resource",
             tags=["resource"],
             include_in_schema=sys_config.expose_gui_api)
async def upsert_resource(resource: Resource):
    return await upsert_resource_cmd(resource)


@router.delete("/resource/{id}",
               tags=["resource"],
               include_in_schema=sys_config.expose_gui_api)
async def delete_resource(id: str):
    return await delete_resource_cmd(id)
