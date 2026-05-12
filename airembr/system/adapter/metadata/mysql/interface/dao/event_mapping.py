from typing import Tuple, Optional, List, Callable

from airembr.system.decorator.proxy.proxy_decorator import cache_proxy, invalidate_cache_proxy
from airembr.system.process.locking.async_locking import async_lock
from airembr.db.preconfig.preconfigured_metadata import pc_event_mapping
from airembr.model.metadata.sys_event_mapping import EventTypeMetadata
from airembr.system.adapter.metadata.mysql.cache.cache_tags import EVENT_MAPPING_TAG
from airembr.system.adapter.metadata.mysql.mapping.event_to_event_mapping import map_to_event_mapping
from airembr.system.adapter.metadata.mysql.service.event_mapping_service import EventMappingService
from airembr.sdk.storage.metadata.query.select_result import SelectResult

ems = EventMappingService()


def _append_pre_config_records(records: SelectResult, mapper, filter: Callable = None) -> Tuple[
    List[EventTypeMetadata], int]:
    if filter:
        pre_config_records = pc_event_mapping.filter_as_list(filter, EventTypeMetadata)
    else:
        pre_config_records = pc_event_mapping.list_as(EventTypeMetadata)

    if not records.exists():
        return pre_config_records, len(pre_config_records)

    resources = pre_config_records
    for record in records.map_to_objects(mapper):
        resources.append(record)

    return resources, records.count() + len(pre_config_records)


async def load_all(search: str = None, limit: int = None, offset: int = None) -> Tuple[List[EventTypeMetadata], int]:
    records = await ems.load_all(search, limit, offset)
    return _append_pre_config_records(records, map_to_event_mapping)


async def load_by_id(event_mapping_id: str) -> Optional[EventTypeMetadata]:
    mapping = pc_event_mapping.get_by_id(event_mapping_id, EventTypeMetadata)

    if mapping:
        return mapping

    record = await ems.load_by_id(event_mapping_id)
    return record.map_to_object(map_to_event_mapping)


async def load_by_event_type(event_type: str, only_enabled: bool = True) -> Tuple[List[EventTypeMetadata], int]:
    records = await ems.load_by_event_type(event_type, only_enabled)
    return _append_pre_config_records(records,
                                      map_to_event_mapping,
                                      filter=lambda m: m.get('event_type', None) == event_type
                                      )


async def load_by_event_types(event_types: List[str], only_enabled: bool = True) -> Tuple[List[EventTypeMetadata], int]:
    records = await ems.load_by_event_types(event_types, only_enabled)
    return _append_pre_config_records(records,
                                      map_to_event_mapping,
                                      filter=lambda m: m.get('event_type', None) in event_types
                                      )


async def load_by_event_type_id(event_type_id: str, only_enabled: bool = True) -> Optional[EventTypeMetadata]:
    event_mapping = pc_event_mapping.get_by_id(event_type_id, EventTypeMetadata)

    if event_mapping:
        return event_mapping

    record = await ems.load_by_event_type_id(event_type_id, only_enabled)
    return record.map_first_to_object(map_to_event_mapping)


# Cached

# @AsyncCache(memory_cache.event_mapping_cache_ttl,
#             timeout=memory_cache.timeout_sql_query_in,
#             max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
#             allow_null_values=True,
#             return_cache_on_error=True
#             )
@cache_proxy(**EVENT_MAPPING_TAG, cache_key_func=lambda args, kwargs: kwargs['event_type_id'])
async def load_event_mapping(event_type_id: str) -> Optional[EventTypeMetadata]:
    async with async_lock('mysql-query'):
        mappings = await load_by_event_type_id(event_type_id, only_enabled=True)
        if not mappings:
            return None
        return mappings


@invalidate_cache_proxy(names=[EVENT_MAPPING_TAG['name']])
async def delete_by_id(event_mapping_id: str) -> Tuple[bool, Optional[EventTypeMetadata]]:
    return await ems.delete_by_id(event_mapping_id)


@invalidate_cache_proxy(names=[EVENT_MAPPING_TAG['name']])
async def insert(event_type_metadata: EventTypeMetadata):
    return await ems.insert(event_type_metadata)
