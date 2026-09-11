from typing import Optional, Tuple

from airembr.core.json.loader import try_json
from airembr.sdk.service.parser.entity_property.entity_query_by_property_parser import (
    EntityQueryByPropertyParser,
    EntityQueryParseError,
)
from airembr.system.adapter.bigdata.big_data_adapter import (
    bd_log_adapter,
    bd_entity_adapter,
    bd_metadata_adapter,
    bd_observation_adapter,
    bd_entity_property_adapter,
)
from airembr.system.command.entity.errors import EntityError


async def get_profile_logs(entity_name: str, entity_id: str, sort: str = None) -> Tuple[list, int]:
    records, total = await bd_log_adapter.load_entity_logs_by_entity_id(entity_name, entity_id, sort=sort)
    return list(records), total


async def count_profiles(entity_name: str) -> int:
    return await bd_entity_adapter.count(entity_name)


async def get_entity_by_hash(entity_type: str, hash: str) -> Optional[dict]:
    # This is acceptable - we see the profile from the database
    return await bd_entity_adapter.load_entity_by_hash(entity_type, hash)


async def get_temporal_entity_by_entity_pk(entity_pk: str, data_hash: str) -> Optional[dict]:
    """
    Temporal entities are entities with traits that were delivered during fact collection.
    They do not contain the current state, only the state at the time of fact collection.
    """
    return await bd_entity_adapter.load_event_entity_by_data_hash_and_ent_pk(entity_pk, data_hash)


async def get_entity_columns(table_name: str) -> list:
    records = await bd_metadata_adapter.list_table_columns(table_name)
    return [
        row['COLUMN_NAME']
        for row in records.list()
    ]


async def list_entities_by_type_page(entity_type: str, page: int):
    return await bd_entity_adapter.load_all_entities(entity_type, page)


async def get_observation_entities_for_observer(observation_id: str, observer_pk: str) -> list:
    return [item async for item in
            bd_entity_adapter.load_observation_entities_for_observer(observation_id, observer_pk)]


async def get_entities_from_observation(observation_id: str) -> list:
    """
    Gets entities for given observation regardless observer
    """

    result = await bd_observation_adapter.load_observations_entities_by_observation_id([observation_id],
                                                                                       order_by="e2o.entity_type")

    result = result >> {
        "entity.pk": "entity_pk",
        "entity.type": "entity_type",
        "entity.label": "label",
        "entity.traits": "traits",
        "entity.stitch_ts": "stitch_ts",
    }

    def _yield_data(result):
        for item in result:
            traits = item.get('entity.traits', None)
            if traits:
                item['entity.traits'] = try_json(traits)
            yield item

    return [item for item in _yield_data(result)]


async def list_entity_snapshots(query: str, entity_type: Optional[str], observer: Optional[str], page: Optional[int]) -> dict:
    query = query.strip()

    if not observer:  # clear all ""
        observer = None

    try:
        parser = EntityQueryByPropertyParser()
        if query and query.strip() != "":
            properties = parser.parse(query)
        else:
            properties = []

        result = await bd_entity_property_adapter.load_entity_by_properties(properties, entity_type, observer, page)
        return {
            "total": len(result),
            "result": result
        }
    except EntityQueryParseError as e:
        raise EntityError(f"Incorrect query: {str(e)}", 500)
