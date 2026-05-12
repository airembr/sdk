from typing import Optional, Tuple, Callable, List

from airembr.system.decorator.proxy.proxy_decorator import cache_proxy, invalidate_cache_proxy
from airembr.system.process.locking.async_locking import async_lock
from airembr.system.adapter.metadata.mysql.cache.cache_tags import EVENT_RESHAPING_TAG
from airembr.db.preconfig.preconfigured_metadata import pc_event_reshaping
from airembr.model.metadata.sys_evt_reshaping import EventReshapingSchema
from airembr.system.adapter.metadata.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping
from airembr.system.adapter.metadata.mysql.service.event_reshaping_service import EventReshapingService
from airembr.sdk.storage.metadata.query.select_result import SelectResult

ers = EventReshapingService()


def _has_event_id(data: dict, event_type) -> bool:
    try:
        return data['event_type'] == event_type
    except (KeyError, TypeError):
        return False


def _append_pre_config_records(records: SelectResult, mapper, filter: Callable = None) -> Tuple[
    List[EventReshapingSchema], int]:
    if filter:
        pre_config_records = pc_event_reshaping.filter_as_list(filter, EventReshapingSchema)
    else:
        pre_config_records = pc_event_reshaping.list_as(EventReshapingSchema)

    if not records.exists():
        return pre_config_records, len(pre_config_records)

    resources = pre_config_records
    for record in records.map_to_objects(mapper):
        resources.append(record)

    return resources, records.count() + len(pre_config_records)


async def load_all_event_reshaping(search: str = None, limit: int = None, offset: int = None) -> Tuple[
    List[EventReshapingSchema], int]:
    records = await ers.load_all(search, limit, offset)
    return _append_pre_config_records(records, map_to_event_reshaping)


async def load_event_reshaping_by_id(event_reshaping_id: str) -> Optional[EventReshapingSchema]:
    event_reshaping = pc_event_reshaping.get_by_id(event_reshaping_id, EventReshapingSchema)

    if event_reshaping:
        return event_reshaping

    records = await ers.load_by_id(event_reshaping_id)

    return records.map_first_to_object(map_to_event_reshaping)


async def load_event_reshaping_by_event_type(event_type: str, only_enabled: bool = True):
    records = await ers.load_by_event_type(event_type, only_enabled)
    return _append_pre_config_records(records,
                                      map_to_event_reshaping,
                                      filter=lambda item: _has_event_id(item, event_type))


# Cache

@cache_proxy(**EVENT_RESHAPING_TAG, cache_key_func=lambda args, kwargs: args[0])
async def load_and_convert_reshaping(event_type: str) -> Optional[List[EventReshapingSchema]]:
    async with async_lock('mysql-query'):
        reshape_schemas, total = await load_event_reshaping_by_event_type(event_type)
        if reshape_schemas:
            return reshape_schemas
        return None


@invalidate_cache_proxy(names=[EVENT_RESHAPING_TAG['name']])
async def delete_event_reshaping_by_id(event_reshaping_id: str) -> Tuple[bool, Optional[EventReshapingSchema]]:
    return await ers.delete_by_id(event_reshaping_id)


@invalidate_cache_proxy(names=[EVENT_RESHAPING_TAG['name']])
async def insert_event_reshaping(event_reshaping: EventReshapingSchema):
    return await ers.insert(event_reshaping)
