from typing import Optional
from fastapi import APIRouter, Depends

from airembr.model.enum.type_enum import TypeEnum
from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_resource import Resource
from airembr.system.command.resource.resource import (
    get_resource_types_list as get_resource_types_list_cmd,
    list_resources_names_by_tag as list_resources_names_by_tag_cmd,
    list_all_resources as list_all_resources_cmd,
    list_resources as list_resources_cmd,
    list_resources_by_type as list_resources_by_type_cmd,
    get_resource_by_id as get_resource_by_id_cmd,
    upsert_resource as upsert_resource_cmd,
    delete_resource as delete_resource_cmd,
)
from airembr_api.endpoint.gui.auth.permissions import Permissions

router = APIRouter()


@router.get("/resources/type/{type}",
            tags=["resource"],
            response_model=dict,
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def resource_types_list(type: TypeEnum) -> dict:
    return await get_resource_types_list_cmd(type)


@router.get("/resources/entity/tag/{tag}",
            tags=["resource"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def list_resources_names_by_tag(tag: str):
    """
    Returns list of resources that have defined tag. This list contains only id and name.
    """
    resources, total = await list_resources_names_by_tag_cmd(tag)

    return {
        "total": total,
        "result": resources
    }


@router.get("/resources/entity",
            tags=["resource"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def list_all_resources():
    resources, total = await list_all_resources_cmd()
    return {
        "total": total,
        "result": resources
    }


@router.get("/resources",
            tags=["resource"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def list_resources():
    resources, total = await list_resources_cmd()
    return {
        "total": total,
        "result": resources
    }


@router.get("/resources/by_type",
            tags=["resource"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def list_resources_by_type(query: str = None, limit: int = 200):
    resources, total = await list_resources_by_type_cmd(query, limit)
    return {
        "total": total,
        "grouped": {"Resources": resources}
    }


@router.get("/resource/{id}",
            tags=["resource"],
            response_model=Optional[Resource],
            dependencies=[Depends(Permissions(roles=["admin", "developer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def get_resource_by_id(id: str) -> Optional[Resource]:
    """
    Returns source data with given id.
    """

    return await get_resource_by_id_cmd(id)


@router.post("/resource",
             tags=["resource"],
             dependencies=[Depends(Permissions(roles=["admin", "developer"]))],
             include_in_schema=sys_config.expose_gui_api)
async def upsert_resource(resource: Resource):
    return await upsert_resource_cmd(resource)


@router.delete("/resource/{id}",
               tags=["resource"],
               dependencies=[Depends(Permissions(roles=["admin", "developer"]))],
               include_in_schema=sys_config.expose_gui_api)
async def delete_resource(id: str):
    return await delete_resource_cmd(id)
