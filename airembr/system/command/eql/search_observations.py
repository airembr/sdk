from datetime import datetime
from typing import Optional

from airembr.model.system.meta_language.meta_lang_model import MetaLangQuery
from airembr.system.adapter.bigdata.big_data_adapter import bd_entity_property_adapter
from airembr.system.command.eql.errors import parse_eql


async def search_observations(eql_model: MetaLangQuery,
                              unmatched_entities: int,
                              unmatched_traits: int,
                              start_date: datetime,
                              end_date: datetime,
                              start: int,
                              limit: int):
    all_results = []
    for and_query in eql_model.yield_leafs(operator='AND'):
        # TODO limit in SQL (use limit from params)
        data = await bd_entity_property_adapter.load_observations_with_eql(
            and_query,
            unmatched_entities=unmatched_entities,
            unmatched_traits=unmatched_traits,
            start_date=start_date,
            end_date=end_date,
        )
        if data:
            all_results.extend(data.list())

    if not all_results:
        return []

    no_of_observations = len(all_results)
    if no_of_observations > 500:
        # Narrow down
        all_results = all_results[:500]

    seen = set()
    unique_results = []
    for obs in all_results:
        obs_id = obs.get('id')
        if obs_id not in seen:
            seen.add(obs_id)
            unique_results.append(obs)

    offset = start or 0
    page_size = limit or 500
    unique_results = unique_results[offset:offset + page_size]

    return unique_results


async def get_observations(query: str,
                           unmatched_entities: Optional[int] = 0,
                           unmatched_traits: Optional[int] = 0,
                           start: Optional[int] = 0,
                           limit: Optional[int] = 500,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> list:
    if not query.strip():
        return []

    eql_model = parse_eql(query)

    return await search_observations(eql_model, unmatched_entities, unmatched_traits, start_date, end_date, start,
                                     limit)
