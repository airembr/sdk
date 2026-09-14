from typing import Optional

from airembr.model.destination_trigger import DestinationTrigger
from airembr.model.metadata.sys_destination import Destination
from airembr.system.adapter.metadata.in_memory.destination_service import DestinationTriggerService
from airembr.system.adapter.metadata.mysql.interface import destination_dao


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


def get_destination_trigger_by_id(trigger_id: str) -> Optional[DestinationTrigger]:
    dts = DestinationTriggerService()
    return dts.load_by_id(trigger_id)


async def delete_destination_by_id(destination_id: str):
    """
    Deletes destination with given id
    """
    await destination_dao.delete_destination(destination_id)

    return True
