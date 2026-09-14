from typing import Optional

from airembr.model.metadata.sys_source import EventSource
from airembr.system.adapter.metadata.mysql.interface import event_source_dao


async def get_event_source_entities(query: str):
    return await event_source_dao.load_event_source_entities(query)


async def list_event_sources(query: str, limit: int):
    return await event_source_dao.load_all_event_sources(query, limit=limit)


async def list_running_event_sources(limit: int):
    """
    Lists all event sources that match given query (str) parameter
    """

    return await event_source_dao.load_active(limit=limit)


def get_event_source_types():
    """
    Returns a list of event source types.
    """
    return event_source_dao.load_event_source_types()


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


async def list_event_sources_names_and_ids(type: Optional[str]):
    """
    Returns list of event sources. This list contains only id and name.
    """

    return await event_source_dao.load_event_source_entities(type)
