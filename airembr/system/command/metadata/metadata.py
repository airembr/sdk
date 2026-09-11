from airembr.core.text.string_manager import capitalize_event_type_id
from airembr.system.adapter.bigdata.big_data_adapter import bd_event_entity_adapter, bd_entity_adapter, bd_metadata_adapter
from airembr.system.adapter.metadata.mysql.interface import entity_object_dao
from airembr.system.service.events import get_event_types, get_event_actors, get_event_traits_by_type


async def get_event_entity_names() -> dict:
    result = await bd_event_entity_adapter.load_event_entity_types(context='entity')
    return {
        "total": len(result),
        "result": [{"id": row, "name": f"{capitalize_event_type_id(row)} ({context})"} for row, context in result]
    }


async def get_entity_object_names() -> dict:
    result = await entity_object_dao.load_entity_types_2()
    return {
        "total": len(result),
        "result": [{"id": row, "name": capitalize_event_type_id(row)} for row in result]
    }


async def get_entity1_types() -> dict:
    result = await bd_entity_adapter.load_entity1_types()
    return {
        "total": len(result),
        "result": [{"id": row, "name": capitalize_event_type_id(row)} for row in result]
    }


async def get_entity_object_properties(entity_type: str, filter: str = None, event_type=None, actor=None,
                                        properties_only=True) -> dict:
    # NOt implemented
    return {
        "total": 0,
        "result": []
    }


async def get_named_event_types(limit: int, entity_type: str):
    """
    Returns event types
    """
    if entity_type:
        entity_type = entity_type.lower()
    return await get_event_types(limit, entity_type)


async def get_named_event_actors(limit: int, entity_type: str):
    """
    Returns event types
    """
    if entity_type:
        entity_type = entity_type.lower()
    return await get_event_actors(limit, entity_type)


async def get_entity_table_columns(table_name: str):
    return await bd_metadata_adapter.list_table_column_names(table_name)


async def get_entity_tables():
    return await bd_metadata_adapter.list_table_names()


async def get_fact_traits_by_type(event_type: str) -> dict:
    if event_type:
        event_type = event_type.lower()

    result = await get_event_traits_by_type(event_type, skip_type=['rel'])

    return {
        "total": len(result),
        "result": result
    }
