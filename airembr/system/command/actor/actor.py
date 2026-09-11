from typing import Optional

from airembr.model.api.request.time_range import DatetimeRangePayload
from airembr.sdk.service.parser.tql.filter_condition import FilterCondition
from airembr.system.adapter.bigdata.big_data_adapter import bd_event_entity_adapter
from airembr.system.adapter.bigdata.general.utils.mapping import entity_history_mapping


def _apply_paging(query: DatetimeRangePayload, page: Optional[int]):
    if page is not None:
        page_size = query.limit
        query.start = page_size * page
        query.limit = page_size


def _apply_where_filter(query: DatetimeRangePayload):
    if query.where:
        parser = FilterCondition(entity_history_mapping())
        query.where = parser.evaluate(query.where)


async def list_actors(query: DatetimeRangePayload, page: Optional[int] = None):
    _apply_paging(query, page)
    _apply_where_filter(query)
    return await bd_event_entity_adapter.load_event_entities(query)


async def get_actors_histogram(query: DatetimeRangePayload):
    _apply_where_filter(query)
    return await bd_event_entity_adapter.load_event_entities_histogram(query)
