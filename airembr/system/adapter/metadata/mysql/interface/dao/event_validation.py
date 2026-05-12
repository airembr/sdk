from typing import Optional, Tuple, List, Callable

from airembr.system.decorator.proxy.proxy_decorator import cache_proxy, invalidate_cache_proxy
from airembr.system.process.locking.async_locking import async_lock
from airembr.db.preconfig.preconfigured_metadata import pc_event_validation
from airembr.model.metadata.sys_evt_validation import EventValidator
from airembr.system.adapter.metadata.mysql.cache.cache_tags import EVENT_VALIDATION_TAG
from airembr.system.adapter.metadata.mysql.mapping.event_validation_mapping import map_to_event_validation
from airembr.system.adapter.metadata.mysql.service.event_validation_service import EventValidationService

evs = EventValidationService()


def _append_pre_config_records(records, mapper, filter: Callable = None) -> Tuple[List[EventValidator], int]:
    if filter:
        pre_config_records = pc_event_validation.filter_as_list(filter, EventValidator)
    else:
        pre_config_records = pc_event_validation.list_as(EventValidator)

    if not records.exists():
        return pre_config_records, len(pre_config_records)

    resources = pre_config_records
    for record in records.map_to_objects(mapper):
        resources.append(record)

    return resources, records.count() + len(pre_config_records)


async def load_all(search: str = None, limit: int = None, offset: int = None) -> Tuple[List[EventValidator], int]:
    records = await evs.load_all(search, limit, offset)
    return _append_pre_config_records(records, map_to_event_validation)


async def load_all_ttls(event_types: List[str] = None) -> Tuple[List[EventValidator], int]:
    records = await evs.load_ttls(event_types)
    return _append_pre_config_records(records, map_to_event_validation)


async def load_by_id(event_validation_id: str) -> Optional[EventValidator]:
    validation = pc_event_validation.get_by_id(event_validation_id, EventValidator)

    if validation:
        return validation

    record = await evs.load_by_id(event_validation_id)
    return record.map_to_object(map_to_event_validation)


async def load_by_event_type(event_type: str, only_enabled: bool = True):
    records = await evs.load_by_event_type(event_type, only_enabled)
    return _append_pre_config_records(records,
                                      map_to_event_validation,
                                      filter=lambda m: m.get('event_type', None) == event_type
                                      )


# Cache
# @AsyncCache(memory_cache.event_validation_cache_ttl,
#             timeout=memory_cache.timeout_sql_query_in,
#             max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
#             return_cache_on_error=True
#             )
@cache_proxy(**EVENT_VALIDATION_TAG, cache_key_func=lambda args, kwargs: args[0])
async def load_event_validation(event_type: str) -> List[EventValidator]:
    async with async_lock('mysql-query'):
        records, _ = await load_by_event_type(event_type, only_enabled=True)
        return records


@invalidate_cache_proxy(names=[EVENT_VALIDATION_TAG['name']])
async def delete_by_id(event_validation_id: str) -> Tuple[bool, Optional[EventValidator]]:
    return await evs.delete_by_id(event_validation_id)


@invalidate_cache_proxy(names=[EVENT_VALIDATION_TAG['name']])
async def insert(event_validation: EventValidator):
    return await evs.insert(event_validation)
