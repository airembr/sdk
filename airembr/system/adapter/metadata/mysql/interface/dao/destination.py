import json
from typing import List, Tuple, Optional, Callable, Generator

from airembr.system.decorator.proxy.proxy_decorator import invalidate_cache_proxy
from airembr.system.adapter.metadata.mysql.mapping.resource_mapping import map_to_resource_from_dict
from airembr.model.metadata.sys_destination import Destination, DestinationConfig
from airembr.system.process.locking.async_locking import async_lock
from airembr.db.preconfig.preconfigured_metadata import pc_destinations
from airembr.system.adapter.metadata.mysql.cache.cache_tags import DESTINATION_TAG
from airembr.system.adapter.metadata.mysql.mapping.destination_mapping import map_to_destination
from airembr.system.adapter.metadata.mysql.service.destination_service import DestinationService
from airembr.model.metadata.sys_resource import Resource, ResourceCredentials
from airembr.sdk.common.map_to_named_entity import map_to_named_entity
from airembr.sdk.storage.metadata.query.select_result import SelectResult

ds = DestinationService()


def _has_event_id(data: dict, event_type) -> bool:
    try:
        return data['event_type']['id'] == event_type
    except (KeyError, TypeError):
        return False


def _append_pre_config_records(records: SelectResult, mapper, filter: Callable = None) -> Tuple[List[Destination], int]:
    if filter:
        pre_config_records = pc_destinations.filter_as_list(filter, Destination)
    else:
        pre_config_records = pc_destinations.list_as(Destination)

    if not records.exists():
        return pre_config_records, len(pre_config_records)

    resources = pre_config_records
    for record in records.map_to_objects(mapper):
        resources.append(record)

    return resources, records.count() + len(pre_config_records)


async def load_destination_by_id(id: str) -> Optional[Destination]:
    destination = pc_destinations.get_by_id(id, Destination)

    if destination:
        return destination

    record = await ds.load_by_id(id)

    if not record.exists():
        return None

    return record.map_to_object(map_to_destination)


async def load_all_destinations(query, start, limit) -> Tuple[List[Destination], int]:
    records = await ds.load_all(query, start, limit)
    return _append_pre_config_records(records,
                                      map_to_destination)


async def load_all_destinations_meta(query, start, limit) -> Tuple[List[Destination], int]:
    records = await ds.load_all(query, start, limit)
    return _append_pre_config_records(records,
                                      map_to_named_entity)


async def _load_enabled_destinations(trigger_type: str, event_type: str = None) -> Tuple[List[Destination], int]:
    records = await ds.load_enabled_destinations(trigger_type, event_type)
    return _append_pre_config_records(records,
                                      map_to_destination)


async def load_destinations_for_event_type(event_type: str, source_id: str) -> Tuple[List[Destination], int]:
    records = await ds.load_event_destinations(event_type, source_id)
    return _append_pre_config_records(records,
                                      map_to_destination,
                                      filter=lambda x: _has_event_id(x, event_type)
                                      )


# async def load_destinations_for_profile():
#     records = await ds.load_profile_destinations()
#     return _append_pre_config_records(records,
#                                       map_to_destination,
#                                       filter=lambda item: item.get('on_profile_change_only', False) is True
#                                       )


# Cache

# @cache_proxy(**DESTINATION_TAG)
async def load_enabled_destinations(trigger_type: str, event_type: str = None) -> List[Destination]:
    async with async_lock('mysql-query'):
        destination, total = await _load_enabled_destinations(trigger_type, event_type)
        return destination


# @cache_proxy(**DESTINATION_TAG)
async def load_event_destinations(event_type, source_id) -> List[Destination]:
    async with async_lock('mysql-query'):
        destination, total = await load_destinations_for_event_type(event_type, source_id)
        return destination


@invalidate_cache_proxy(names=[DESTINATION_TAG['name']])
async def insert_destination(destination: Destination):
    return await ds.insert(destination)


@invalidate_cache_proxy(names=[DESTINATION_TAG['name']])
async def delete_destination(id: str):
    await ds.delete_by_id(id)


async def load_destination_resources():
    return await ds.load_destination_resources()


def yield_enabled_destination_resources(records) -> Generator:
    for record in records:
        if record.get('resource_type') == 'workflow':
            yield Resource(**{
                "id": record['id'],
                "name": record['name'],
                "production": record['production'],
                "type": "workflow",
                "timestamp": record['timestamp'],
                "description": record['description'],
                "credentials": ResourceCredentials(),
                "tags": record['tags'],
                "groups": [],
                "icon": 'flow',
                "destination": DestinationConfig(**{
                    "package":"airembr.system.process.dispatching.plugin.workflow_connector.WorkflowConnector",
                    "init":{},
                    "form":{},
                    "outbound":"workflow"
                }),
                "enabled": record['enabled'],
                "locked": record['locked']
            })

        elif record.get('resource_type') == 'resource':
            yield map_to_resource_from_dict({
                "id": record['id'],
                "name": record['name'],
                "production": record['production'],
                "type": "workflow",
                "timestamp": record['timestamp'],
                "description": record['description'],
                "credentials": record['credentials'],
                "tags": record['tags'],
                "groups": record['groups'],
                "icon": record['icon'],
                "destination": json.loads(record['destination']) if isinstance(record['destination'], str) else None,
                "enabled": record['enabled'],
                "locked": record['locked']
            })
