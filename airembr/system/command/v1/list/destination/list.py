from typing import Dict

from airembr.model.metadata.sys_resource import Resource
from airembr.system.adapter.metadata.in_memory.destination_service import DestinationTriggerService
from airembr.system.adapter.metadata.mysql.interface import destination_dao
from airembr.system.process.dispatching.utils import get_destination_types


async def get_destinations_type_list() -> dict:
    """
    Returns destination types.
    """
    return {key: value for key, value in get_destination_types()}


async def get_destinations_by_tag(query: str, start: int, limit: int):
    return await destination_dao.load_all_destinations(query, start, limit)


async def get_destinations_meta(query: str, start: int, limit: int):
    return await destination_dao.load_all_destinations_meta(query, start, limit)


def get_destination_triggers_metadata() -> dict:
    dts = DestinationTriggerService()
    triggers = [
        {
            "id": item.id,
            "name": item.name
        } for item in dts.load_all()
    ]
    return {
        "total": len(triggers),
        "result": sorted(triggers, key=lambda x: x['name'])
    }


async def list_destination_resources() -> Dict[str, Resource]:
    records = await destination_dao.load_destination_resources()
    result = destination_dao.yield_enabled_destination_resources(records.values())
    return {resource.id: resource for resource in result}
