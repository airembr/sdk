from typing import Optional

from airembr.system.adapter.metadata.mysql.interface import resource_dao
from airembr.system.preconfig.setup_resources import get_type_of_resources


async def list_resources_by_id() -> dict:
    resources = sorted(list(get_type_of_resources()), key=lambda x: x[0])

    resource_types = {id: value for id, value in resources}

    return {
        "total": len(resource_types),
        "result": resource_types
    }


async def list_resources_metadata() -> dict:
    resources = sorted(list(get_type_of_resources()), key=lambda x: x[0])

    resource_types = {id: value['name'] for id, value in resources}

    return {
        "total": len(resource_types),
        "result": resource_types
    }


async def list_resources_names_by_tag(tag: str):
    """
    Returns list of resources that have defined tag. This list contains only id and name.
    """
    return await resource_dao.load_resources_entities_by_tag(tag)


async def list_all_resources():
    return await resource_dao.load_all_resource_entities(limit=250)


# async def list_resources():
#     return await resource_dao.load_all_resources()


async def list_resources(query: Optional[str]=None, limit: Optional[int]=250):
    if query is None:
        return await resource_dao.load_all_resource_entities(limit=250)
    return await resource_dao.load_all_resources(search=query, limit=limit)
