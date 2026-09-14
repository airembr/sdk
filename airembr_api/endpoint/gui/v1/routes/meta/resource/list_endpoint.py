from typing import Optional

from fastapi import APIRouter, Depends

from airembr.system.config.sys_config import sys_config
from airembr.system.command.v1.list.resource.list import (
    list_resources_by_id as list_resources_by_id_cmd,
    list_resources_names_by_tag as list_resources_names_by_tag_cmd,
    list_resources as list_resources_cmd, list_resources_metadata,
)
from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

router = APIRouter()


@router.get("/v1/resources",
            tags=["v1/resource"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def list_resources_by_type(query: Optional[str] = None, limit: int = 200):
    resources, total = await list_resources_cmd(query, limit)
    return {
        "total": total,
        "grouped": {"Resources": resources}
    }


@router.get("/v1/resources/config",
            tags=["v1/resource"],
            response_model=dict,
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def list_resources_as_id_and_full_object() -> dict:
    """
    Returns a list of resource ids and full configuration objects.
    """
    return await list_resources_by_id_cmd()


@router.get("/v1/resources/meta",
            tags=["v1/resource"],
            response_model=dict,
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def list_resource_as_id_and_name() -> dict:
    return await list_resources_metadata()


@router.get("/v1/resources/meta/by-tag/{tag}",
            tags=["v1/resource"],
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

# @router.get("/resources/entity",
#             tags=["resource"],
#             dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
#             include_in_schema=sys_config.expose_gui_api)
# async def list_all_resources():
#     resources, total = await list_resources_cmd()
#     return {
#         "total": total,
#         "result": resources
#     }


# @router.get("/resources",
#             tags=["resource"],
#             dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
#             include_in_schema=sys_config.expose_gui_api)
# async def list_resources():
#     resources, total = await list_resources_cmd()
#     return {
#         "total": total,
#         "result": resources
#     }
