from typing import Optional

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


async def list_event_sources_names_and_ids(type: Optional[str]):
    """
    Returns list of event sources. This list contains only id and name.
    """

    return await event_source_dao.load_event_source_entities(type)
