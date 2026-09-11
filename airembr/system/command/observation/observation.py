from typing import Optional

from airembr.model.api.request.time_range import DatetimeRangePayload
from airembr.model.payload.query_result import QueryResult
from airembr.sdk.service.parser.tql.filter_condition import FilterCondition
from airembr.system.adapter.bigdata.big_data_adapter import bd_observation_adapter, bd_event_entity_adapter
from airembr.system.adapter.bigdata.general.utils.mapping import sys_obs_mapping


def _apply_where_filter(query: DatetimeRangePayload):
    if query.where:
        parser = FilterCondition(sys_obs_mapping())
        query.where = parser.evaluate(query.where)


async def get_observation(observation_id: str) -> list:
    observation_id = observation_id.strip()
    result = await bd_observation_adapter.load_observation_by_id(observation_id)
    return result.list()


async def get_observation_facts(observation_id: str, start: Optional[int], limit: Optional[int]) -> list:
    observation_id = observation_id.strip()
    result = await bd_observation_adapter.load_facts_by_observation_id(observation_id, start, limit)
    return result.list()


async def delete_observation(observation_id: str):
    observation_id = observation_id.strip()
    await bd_observation_adapter.delete_observation_by_id(observation_id)


async def get_observers_from_facts() -> dict:
    """
    Retrieves a list of observers based on stored event entity facts.

    This function fetches and returns a collection of unique primary keys of observers
    (identifiers) corresponding to the event entity observers.

    Returns:
        list: A list of unique primary keys for event entity observers.
    """
    result = await bd_event_entity_adapter.load_event_entity_observer_pks()

    return {
        "total": len(result),
        "result": result
    }


async def load_observations() -> QueryResult:
    result = await bd_observation_adapter.load_observations()
    if not result:
        return QueryResult(total=0, result=[])
    count = await bd_observation_adapter.count_observations()
    return QueryResult(total=count, result=result.list(cast_to=dict))


async def load_observations_by_query(query: DatetimeRangePayload, page: Optional[int]) -> QueryResult:
    if page is not None:
        page_size = query.limit
        query.start = page_size * page
        query.limit = page_size

    _apply_where_filter(query)

    result = await bd_observation_adapter.load_observations_by_query(query)
    if not result:
        return QueryResult(total=0, result=[])

    count = await bd_observation_adapter.count_observations_by_query(query)
    return QueryResult(total=count, result=result.list(cast_to=dict))


async def get_observations_histogram(query: DatetimeRangePayload):
    _apply_where_filter(query)
    return await bd_observation_adapter.load_observations_histogram(query)
