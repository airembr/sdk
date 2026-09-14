from typing import Optional

from airembr.model.metadata.sys_source import EventSource
from airembr.system.adapter.metadata.mysql.interface import event_source_dao


async def load_source_by_id(source_id: str) -> Optional[EventSource]:
    """
    Returns event source with given ID (str)
    """
    return await event_source_dao.load_event_source_by_id(source_id)


async def save_event_source(source: EventSource):
    """
    Adds new event source in database
    """
    return await event_source_dao.insert_event_source(source)


async def delete_event_source(source_id: str):
    """
    Deletes event source with given ID (str).
    Return False if it is available in draft or production. True if all the instances where deleted
    """

    return await event_source_dao.delete_event_source(source_id)
