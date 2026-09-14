from typing import Optional, Tuple

from airembr.model.entity_object import EntityObject
from airembr.system.adapter.bigdata.big_data_adapter import (
    bd_observation_adapter,
    bd_event_entity_adapter,
    bd_event_adapter,
    bd_entity_stitch_adapter,
    bd_entity_property_state_adapter,
)
from airembr.system.adapter.metadata.mysql.interface import entity_object_dao


async def get_entity_observations(entity_pk: str) -> list:
    result = await bd_observation_adapter.load_observations_by_entity_pk(entity_pk)
    return (result >> {
        "metadata.time.create": "metadata_time_create",
        "metadata.time.insert": "metadata_time_insert",
        "description": "description",
        "summary": "summary",
    }).list()


async def list_entity_objects(query: Optional[str], start: int, limit: int) -> Tuple[list, int]:
    return await entity_object_dao.load_all(query, limit, start)


async def get_entity_texts(entity_pk: str) -> list:
    entity_descriptions = await bd_observation_adapter.load_entity_descriptions(entity_pks=[entity_pk])
    return entity_descriptions.list()


async def list_entity_tables() -> list:
    records = await entity_object_dao.load_all_with_tables()
    if not records:
        return []
    return [{"entity": row.type.capitalize(), "table": row.table} for row in records]


async def save_entity_object(entity_object: EntityObject):
    if not entity_object.table:
        entity_object.remove_property_columns()

    # Clear from the FK that cannot be saved
    allowed_properties = {prop.name for prop in entity_object.properties if prop.name}
    allowed_stitches = [stitch for stitch in entity_object.stitches if stitch.entity_property in allowed_properties]
    entity_object.stitches = allowed_stitches

    await entity_object_dao.insert(entity_object)


async def get_entity_object_payload(entity_type_id: str) -> Optional[EntityObject]:
    entity_type_id = entity_type_id.lower()
    return await entity_object_dao.load_entity_type_by_id(entity_type_id)


async def delete_entity_object(entity_type_id: str):
    return await entity_object_dao.delete_by_id(entity_type_id)


async def get_entity_history(entity_id: str) -> list:
    return await bd_event_entity_adapter.load_entity_history_by_id(entity_id, order='DESC')


async def load_events_by_data_hash(data_hash: str) -> list:
    return await bd_event_adapter.load_events_by_data_hash(data_hash)


async def get_entity_object_current_state(entity_pk: str, observer_pk: Optional[str] = None):
    entity_pk = entity_pk.strip()
    stitched_data = await bd_entity_stitch_adapter.load_pks_stitched_by_iid(entity_pk)
    stitched_pks = {item['entity_pk'] for item in stitched_data}
    if not stitched_pks:
        # There is no stitching, so we can return the entity state by searching entity_pk
        return await bd_entity_property_state_adapter.load_entity_state_by_entity_pk(entity_pk)

    if len(stitched_pks) < 100:
        # There is stitching, so we need to return the state of the stitched entity
        return await bd_entity_property_state_adapter.load_entity_state_by_entity_pks(stitched_pks, observer_pk)

    # If the stitching is big use gid and view not all stitched pks
    stitched_iids = {item['entity_gid'] for item in stitched_data}
    return await bd_entity_property_state_adapter.load_entity_state_by_entity_iid(stitched_iids, observer_pk)
