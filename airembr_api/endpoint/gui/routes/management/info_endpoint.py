from fastapi import APIRouter

from airembr_api.service.grouping import get_grouped_result
from airembr.system.adapter.metadata.mysql.mapping.version_mapping import map_to_version
from airembr.system.config.sys_config import sys_config
from airembr.system.command.info.info import (
    list_versions as list_versions_cmd,
    get_version as get_version_cmd,
    get_current_backend_version as get_current_backend_version_cmd,
)

router = APIRouter()


@router.get("/info/versions", tags=["info"], include_in_schema=sys_config.expose_gui_api)
async def get_versions():
    """
    Returns info about Tracardi Installed Versions
    """

    records = await list_versions_cmd()
    return get_grouped_result("Versions", records, map_to_version)


@router.get("/info/version", tags=["info"], include_in_schema=sys_config.expose_gui_api, response_model=str)
async def get_version():
    """
    Returns info about Tracardi API version
    """
    return await get_version_cmd()


@router.get("/info/version/details", tags=["info"])
@router.get("/")
async def get_current_backend_version():
    """
    Returns current backend version with previous versions.
    """
    return await get_current_backend_version_cmd()
