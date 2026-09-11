from fastapi import APIRouter, Depends
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.metadata.metadata import (
    get_event_entity_names as get_event_entity_names_cmd,
    get_entity_object_names as get_entity_object_names_cmd,
    get_entity1_types as get_entity1_types_cmd,
    get_entity_object_properties as get_entity_object_properties_cmd,
    get_named_event_types as get_named_event_types_cmd,
    get_named_event_actors as get_named_event_actors_cmd,
    get_entity_table_columns as get_entity_table_columns_cmd,
    get_entity_tables as get_entity_tables_cmd,
    get_fact_traits_by_type as get_fact_traits_by_type_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))]
)


@router.get("/v2/named/event/entities", tags=["v2/metadata"], include_in_schema=sys_config.expose_gui_api)
async def get_event_entity_names():
    return await get_event_entity_names_cmd()


@router.get("/v2/named/entities/2", tags=["v2/metadata"], include_in_schema=sys_config.expose_gui_api)
async def get_entity_object_names():
    return await get_entity_object_names_cmd()


@router.get("/v2/named/entities/1", tags=["v2/metadata"], include_in_schema=sys_config.expose_gui_api)
async def get_entity1_types():
    return await get_entity1_types_cmd()


# TODO NOt used -check
@router.get("/v2/named/entity/{entity_type}/properties", tags=["v2/metadata"],
            include_in_schema=sys_config.expose_gui_api)
async def get_entity_object_properties(entity_type: str, filter: str = None, event_type=None, actor=None,
                                  properties_only=True):
    return await get_entity_object_properties_cmd(entity_type, filter, event_type, actor, properties_only)


@router.get("/v2/named/event/types", tags=["v2/metadata"], include_in_schema=sys_config.expose_gui_api)
# @router.get("/events/metadata/type", tags=["metadata"], include_in_schema=sys_config.expose_gui_api)
async def get_named_event_types(limit: int = 1000, entity_type: str = None):
    """
    Returns event types
    """
    return await get_named_event_types_cmd(limit, entity_type)


@router.get("/v2/named/event/actors", tags=["v2/metadata"], include_in_schema=sys_config.expose_gui_api)
async def get_named_event_actors(limit: int = 1000, entity_type: str = None):
    """
    Returns event types
    """
    return await get_named_event_actors_cmd(limit, entity_type)


# TODO NOt used -check
@router.get("/v2/named/table/{table_name}/columns", tags=["v2/metadata"], include_in_schema=sys_config.expose_gui_api)
async def get_entity_table_columns(table_name: str):
    return await get_entity_table_columns_cmd(table_name)


# TODO NOt used -check
@router.get("/v2/named/tables", tags=["v2/metadata"], include_in_schema=sys_config.expose_gui_api)
async def get_entity_tables():
    return await get_entity_tables_cmd()


@router.get("/v2/fact/traits/by/type", tags=["v2/metadata"], include_in_schema=sys_config.expose_gui_api)
async def get_fact_traits_by_type(event_type: str):
    return await get_fact_traits_by_type_cmd(event_type)
