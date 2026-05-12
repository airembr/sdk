from typing import Tuple, List, Optional, Callable

from airembr.system.decorator.proxy.proxy_decorator import invalidate_cache_proxy, cache_proxy
from airembr.db.preconfig.preconfigured_metadata import pc_resources
from airembr.model.metadata.sys_resource import Resource
from airembr.system.adapter.metadata.mysql.cache.cache_tags import RESOURCE_TAG
from airembr.sdk.common.map_to_named_entity import map_to_named_entity
from airembr.system.adapter.metadata.mysql.mapping.resource_mapping import map_to_resource
from airembr.system.adapter.metadata.mysql.service.resource_service import ResourceService

rs = ResourceService()


def _append_pre_config_records(records, mapper, filter: Callable = None) -> Tuple[List[Resource], int]:
    if filter:
        pre_config_records = pc_resources.filter_as_list(filter, Resource)
    else:
        pre_config_records = pc_resources.list_as(Resource)

    if not records.exists():
        return pre_config_records, len(pre_config_records)

    resources = pre_config_records
    for record in records.map_to_objects(mapper):
        resources.append(record)

    return resources, records.count() + len(pre_config_records)


async def load_resource_by_id(resource_id: str) -> Optional[Resource]:
    resource = pc_resources.get_by_id(resource_id, Resource)

    if resource:
        return resource

    record = await rs.load_by_id(resource_id)
    return record.map_to_object(map_to_resource)


async def load_resource_by_id_with_error(resource_id: str) -> Optional[Resource]:
    resource = pc_resources.get_by_id(resource_id, Resource)

    if resource:
        return resource

    resource = (await rs.load_by_id(resource_id)).map_to_object(map_to_resource)

    if resource is None or not resource.enabled:
        return None

    return resource


async def load_all_resources(search: str = None, limit: int = None, offset: int = None) -> Tuple[List[Resource], int]:
    records = await rs.load_all(search, limit, offset)
    return _append_pre_config_records(records, map_to_resource)


async def load_all_resource_entities(search: str = None, limit: int = None, offset: int = None) -> Tuple[
    List[Resource], int]:
    records = await rs.load_all(search, limit, offset)
    return _append_pre_config_records(records, map_to_named_entity)


async def load_resources_entities_by_tag(tag: str) -> Tuple[
    List[Resource], int]:
    records = await rs.load_enabled_by_tag(tag)
    return _append_pre_config_records(records,
                                      map_to_named_entity,
                                      filter=lambda resource: 'tags' in resource and tag in resource['tags'])


# Cache
@cache_proxy(**RESOURCE_TAG)
async def load_resource_via_cache(resource_id: str) -> Optional[Resource]:
    return await load_resource_by_id_with_error(resource_id)


@invalidate_cache_proxy(names=[RESOURCE_TAG['name']])
async def insert_resource(resource: Resource):
    return await rs.insert(resource)


async def delete_resource_by_id(resource_id: str):
    await rs.delete_by_id(resource_id)
