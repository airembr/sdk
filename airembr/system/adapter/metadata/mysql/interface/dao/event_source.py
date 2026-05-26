from typing import List, Tuple, Optional, Dict, Callable

from airembr.system.decorator.proxy.proxy_decorator import invalidate_cache_proxy
from airembr.system.process.locking.async_locking import async_lock
from airembr.system.adapter.metadata.mysql.cache.cache_tags import EVENT_SOURCE_TAG
from airembr.db.preconfig.preconfigured_metadata import pc_event_sources
from airembr.model.metadata.sys_source import EventSource
from airembr.model.system.named_entity import NamedEntity
from airembr.system.adapter.metadata.mysql.mapping.event_source_mapping import map_to_event_source
from airembr.system.adapter.metadata.mysql.service.event_source_service import EventSourceService

ess = EventSourceService()


def _append_pre_config_records(records, mapper, filter: Callable = None) -> Tuple[List[EventSource], int]:
    if filter:
        pre_config_records = pc_event_sources.filter_as_list(filter, EventSource)
    else:
        pre_config_records = pc_event_sources.list_as(EventSource)

    if not records.exists():
        return pre_config_records, len(pre_config_records)

    resources = pre_config_records
    for record in records.map_to_objects(mapper):
        resources.append(record)

    return resources, records.count() + len(pre_config_records)


async def lock_event_source_by_id(service_id, lock: bool):
    await ess.lock_by_bridge_id(service_id, lock=lock)


async def load_active(limit: int) -> Tuple[List[EventSource], int]:
    records = await ess.load_active(limit)
    return _append_pre_config_records(records, map_to_event_source)


async def load_active_event_sources_by_type(bridge_type: str) -> Tuple[List[EventSource], int]:
    records = await ess.load_active_by_bridge_type(bridge_type)

    event_sources = list(records.map_to_objects(map_to_event_source))
    return event_sources, len(event_sources)


async def load_event_source_by_id(source_id) -> Optional[EventSource]:
    event_source = pc_event_sources.get_by_id(source_id, EventSource)

    if event_source:
        return event_source

    record = await ess.load_by_id_in_deployment_mode(source_id)

    if not record.exists():
        return None

    return record.map_to_object(map_to_event_source)


async def load_all_event_sources(query, limit) -> Tuple[List[EventSource], int]:
    records = await ess.load_all_in_deployment_mode(query, limit=limit)
    return _append_pre_config_records(records, map_to_event_source)


def load_event_source_types() -> Tuple[Dict[str, str], int]:
    types = ess.event_source_types()
    types = {id: item['name'] for id, item in types.items()}

    return types, len(types)


async def load_event_source_entities(type: Optional[str] = None) -> Tuple[
    List[NamedEntity], int]:
    predefined_names_entities = pc_event_sources.list_as(NamedEntity)

    if type:
        records = await ess.load_by_type_in_deployment_mode(type)
    else:
        records = await ess.load_all_in_deployment_mode()

    if not records.exists():
        return predefined_names_entities, len(predefined_names_entities)

    total = records.count()
    result = records.as_named_entities(rewriter=lambda r: f"{r.name} ({r.type})")

    if predefined_names_entities:
        result.extend(predefined_names_entities)

    return result, total


# Cache

# @cache_proxy(**EVENT_SOURCE_TAG,
#              cache_key_func=lambda args, kwargs: args[0])
async def load_event_source_via_cache(source_id) -> Optional[EventSource]:
    async with async_lock('mysql-query'):
        return await load_event_source_by_id(source_id)


@invalidate_cache_proxy(names=[EVENT_SOURCE_TAG['name']])
async def delete_event_source(source_id: str):
    await ess.delete_by_id_in_deployment_mode(source_id)


@invalidate_cache_proxy(names=[EVENT_SOURCE_TAG['name']])
async def insert_event_source(event_source: EventSource):
    return await ess.save(event_source)
