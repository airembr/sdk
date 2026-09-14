from typing import Optional

from airembr.model.metadata.sys_resource import Resource
from airembr.system.adapter.metadata.mysql.interface import resource_dao


async def get_resource_by_id(resource_id: str) -> Optional[Resource]:
    """
    Returns source data with given id.
    """

    return await resource_dao.load_resource_by_id(resource_id)


async def upsert_resource(resource: Resource):
    return await resource_dao.insert_resource(resource)


async def delete_resource(resource_id: str):
    return await resource_dao.delete_resource_by_id(resource_id)
