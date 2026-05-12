import json
from datetime import datetime

from airembr.model.system.context import get_context
from airembr.core.security.b64 import encrypt, decrypt
from airembr.model.metadata.sys_resource import Resource, ResourceCredentials
from airembr.system.adapter.metadata.mysql.mapping.utils import split_list
from airembr.system.adapter.metadata.mysql.schema.table import ResourceTable
from airembr.model.metadata.sys_destination import DestinationConfig

def map_to_resource_table(resource: Resource) -> ResourceTable:
    context = get_context()
    return ResourceTable(
        id=resource.id,
        tenant=context.tenant,
        production=context.production,
        type=resource.type,
        timestamp=resource.timestamp or datetime.utcnow(),
        name=resource.name,
        description=resource.description,
        credentials=encrypt(resource.credentials) if resource.credentials else None,
        enabled=resource.enabled,
        locked=resource.locked,
        tags=",".join(resource.tags) if isinstance(resource.tags, list) else resource.tags,
        groups=",".join(resource.groups) if isinstance(resource.groups, list) else resource.groups,
        icon=resource.icon,
        destination=resource.destination.model_dump_json() if resource.destination else None
    )


def map_to_resource(resource_table: ResourceTable) -> Resource:
    credentials = decrypt(resource_table.credentials) if resource_table.credentials else {"production": {}, "test": {}}
    destination = DestinationConfig(**json.loads(resource_table.destination)) if resource_table.destination else None
    return Resource(
        id=resource_table.id,
        name=resource_table.name,
        timestamp=resource_table.timestamp,
        description=resource_table.description,
        type=resource_table.type,
        tags=split_list(resource_table.tags),
        destination=destination,
        groups=split_list(resource_table.groups),
        icon=resource_table.icon,
        enabled=resource_table.enabled,
        locked=resource_table.locked,
        credentials=ResourceCredentials(**credentials),

        production=resource_table.production,
        running=resource_table.running
    )

def map_to_resource_from_dict(resource_dict: dict) -> Resource:
    credentials = decrypt(resource_dict['credentials']) if resource_dict.get('credentials', None) else {"production": {}, "test": {}}
    destination = DestinationConfig(**json.loads(resource_dict['destination'])) if resource_dict.get('destination', None) else None
    return Resource(
        id=resource_dict['id'],
        name=resource_dict['name'],
        timestamp=resource_dict['timestamp'],
        description=resource_dict['description'],
        type=resource_dict['type'],
        tags=split_list(resource_dict['tags']),
        destination=destination,
        groups=split_list(resource_dict['groups']),
        icon=resource_dict['icon'],
        enabled=resource_dict['enabled'],
        credentials=ResourceCredentials(**credentials),

        production=resource_dict['production'],
        running=False
    )
