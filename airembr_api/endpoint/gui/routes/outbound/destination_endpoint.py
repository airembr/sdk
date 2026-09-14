from typing import Dict
from fastapi import APIRouter, Depends
from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

from airembr.model.destination_trigger import DestinationTrigger
from airembr.model.metadata.sys_resource import Resource
from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.command.destination.destination import (
    get_destinations_type_list as get_destinations_type_list_cmd,
    get_destinations_by_tag as get_destinations_by_tag_cmd,
    get_destinations_meta as get_destinations_meta_cmd,
    get_destination_triggers_metadata as get_destination_triggers_metadata_cmd,
    get_destination_trigger_by_id as get_destination_trigger_by_id_cmd,
    list_destination_resources as list_destination_resources_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/destinations/type", tags=["destination"], response_model=dict, include_in_schema=sys_config.expose_gui_api)
async def get_destinations_type_list():
    """
    Returns destination types.
    """
    return await get_destinations_type_list_cmd()


@router.get("/destinations/by_tag", tags=["destination"], response_model=dict,
            include_in_schema=sys_config.expose_gui_api)
async def get_destinations_by_tag(query: str = None, start: int = 0, limit: int = 100) -> dict:
    destinations, total = await get_destinations_by_tag_cmd(query, start, limit)

    return {
        "total": total,
        "grouped": {
            "Triggers": destinations
        },
        "cache": memory_cache_config.destination_cache_ttl
    }


@router.get("/v2/destinations/meta", tags=["destination"], response_model=dict,
            include_in_schema=sys_config.expose_gui_api)
async def get_destinations_meta(query: str = None, start: int = 0, limit: int = 100) -> dict:
    destinations, total = await get_destinations_meta_cmd(query, start, limit)
    return {
        "total": total,
        "result": destinations
    }


@router.get("/v2/destinations/trigger/meta", tags=["destination"], response_model=dict,
            include_in_schema=sys_config.expose_gui_api)
def get_destination_triggers_metadata() -> dict:
    return get_destination_triggers_metadata_cmd()


@router.get("/v2/destination/trigger/{trigger_id}", tags=["destination"], response_model=DestinationTrigger,
            include_in_schema=sys_config.expose_gui_api)
def get_destination_trigger_by_id(trigger_id: str) -> DestinationTrigger:
    return get_destination_trigger_by_id_cmd(trigger_id)


@router.get("/v2/destination/resources/meta",
            tags=["resource"],
            response_model=Dict[str, Resource],
            include_in_schema=sys_config.expose_gui_api)
async def list_destination_resources():
    return await list_destination_resources_cmd()
