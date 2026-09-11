from typing import Optional, Dict

from airembr.model.destination_trigger import DestinationTrigger
from airembr.model.metadata.sys_destination import Destination
from airembr.model.metadata.sys_resource import Resource
from airembr.system.adapter.metadata.in_memory.destination_service import DestinationTriggerService
from airembr.system.adapter.metadata.mysql.interface import destination_dao
from airembr.system.process.dispatching.utils import get_destination_types


async def save_destination(destination: Destination):
    """
    Upserts destination data.
    """
    await destination_dao.insert_destination(destination)


async def get_destination(destination_id: str) -> Optional[Destination]:
    """
    Returns destination or None if destination does not exist.
    """
    return await destination_dao.load_destination_by_id(destination_id)


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


def get_destination_trigger_by_id(trigger_id: str) -> DestinationTrigger:
    dts = DestinationTriggerService()
    return dts.load_by_id(trigger_id)


async def delete_destination_by_id(destination_id: str):
    """
    Deletes destination with given id
    """
    await destination_dao.delete_destination(destination_id)

    return True


async def list_destination_resources() -> Dict[str, Resource]:
    records = await destination_dao.load_destination_resources()
    result = destination_dao.yield_enabled_destination_resources(records.values())
    return {resource.id: resource for resource in result}
