from typing import Optional

from airembr.model.api.request.time_range import DatetimeRangePayload
from airembr.sdk.service.parser.tql.filter_condition import FilterCondition
from airembr.system.adapter.bigdata.big_data_adapter import bd_event_adapter
from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping
from airembr.system.service.events import get_default_event_type_schema


def _shorten_texts(row):
    summary = row.get_or_none("semantic.summary")
    description = row.get_or_none("semantic.description")
    if summary is not None and len(summary) > 150:
        row["semantic.summary"] = f"{summary[:150]}..."
    if description is not None and len(description) > 200:
        row["semantic.description"] = f"{description[:200]}..."

    return row.to_dict()


def _apply_where_filter(query: DatetimeRangePayload):
    if query.where:
        parser = FilterCondition(event_mapping())
        query.where = parser.evaluate(query.where)


async def load_event_by_query(query: DatetimeRangePayload, page: Optional[int], shorten: bool):
    if page is not None:
        page_size = query.limit
        query.start = page_size * page
        query.limit = page_size

    _apply_where_filter(query)

    if shorten:
        return await bd_event_adapter.search_and_process_all(query, function=_shorten_texts)

    return await bd_event_adapter.search_all(query)


async def get_event_histogram(query: DatetimeRangePayload):
    _apply_where_filter(query)
    return await bd_event_adapter.load_events_histogram(query)


async def get_event(event_id: str):
    return await bd_event_adapter.load_event_by_id(event_id)


async def delete_event(event_id: str):
    """
    Deletes event with given ID
    """
    return await bd_event_adapter.delete_event_from_db(event_id)


async def get_events_for_actor_entity(entity_pk: str, limit: int):
    # TODO may need merging
    return await bd_event_adapter.load_events_by_actor_pks(
        entity_pks=[entity_pk],  # Here should be a list of entity_pks (merged)
        limit=limit)


async def get_events_for_object_entity(entity_pk: str, limit: int):
    return await bd_event_adapter.load_events_by_object_pks(
        entity_pks=[entity_pk],  # Here should be a list of entity_pks (merged)
        limit=limit)


async def get_event_type_data_schema(event_type: str, entity_name: str):
    """Gets pre-defined event type data schema"""
    return get_default_event_type_schema(event_type, entity_name)
