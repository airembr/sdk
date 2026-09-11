from datetime import datetime
from typing import List, Optional, Tuple

from airembr.core.dictionary.sorter import sort_dicts_by_id_order
from airembr.model.system.meta_language.meta_lang_model import MetaLangQuery
from airembr.system.adapter.bigdata.big_data_adapter import bd_entity_property_adapter, bd_observation_adapter
from airembr.system.command.eql.errors import EqlError, parse_eql


async def search_fact(eql_model: MetaLangQuery,
                      unmatched_entities: int,
                      unmatched_traits: int,
                      start_date: Optional[datetime],
                      end_date: Optional[datetime],
                      start: int,
                      limit: int
                      ) -> Tuple[List[str], List[dict]]:
    matching_observations = []
    matching_entities = []
    for and_query in eql_model.yield_leafs(operator='AND'):
        # Find all observations that have all entities from query
        async for observation, entity_pks, rank in bd_entity_property_adapter.yield_exact_entities_with_eql(
                and_query,
                unmatched_entities,
                unmatched_traits,
                start_date=start_date,
                end_date=end_date
        ):
            matching_entities.extend(entity_pks)
            matching_observations.append(observation)

    matching_entities = list(set(matching_entities))
    uniq_observation_ids = list(set(matching_observations))

    if not matching_observations:
        return [], []

    no_of_observations = len(matching_observations)
    if no_of_observations > 500:
        raise EqlError(
            detail=f"Too many observations. Over {no_of_observations} observations.Please narrow down your query.",
            status_code=413)

    facts = await bd_observation_adapter.load_facts_by_observation_ids_and_entity_pks(
        uniq_observation_ids,
        matching_entities,
        start,
        limit
    )

    # Sort by the rank order of the observations
    facts = sort_dicts_by_id_order(facts.list(), matching_observations, sort_key='observation.id')

    if not facts:
        # No facts found. Return full observations.
        result = await bd_observation_adapter.load_facts_by_observation_ids(uniq_observation_ids, start,
                                                                            limit)

        # Sort by the rank order of the observations
        facts = sort_dicts_by_id_order(result.list(), matching_observations, sort_key='observation.id')

    return uniq_observation_ids, facts


async def get_observation_facts(query: str,
                                unmatched_entities: int = 0,
                                unmatched_traits: int = 0,
                                start: int = 0,
                                limit: int = 500,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> List[dict]:
    if not query.strip():
        return []

    eql_model = parse_eql(query)
    _, facts = await search_fact(eql_model, unmatched_entities, unmatched_traits, start_date, end_date, start, limit)
    return facts
