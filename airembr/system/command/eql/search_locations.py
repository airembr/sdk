import json
from datetime import datetime
from typing import List, Optional

from airembr.model.system.meta_language.meta_lang_model import MetaLangEntity, MetaLangQuery
from airembr.system.adapter.bigdata.big_data_adapter import bd_entity_property_adapter
from airembr.system.command.eql.errors import parse_eql


async def search_observation_location(eql_model: MetaLangQuery,
                                      entity_types: List[str],
                                      unmatched_entities: int,
                                      unmatched_traits: int,
                                      start_date: datetime,
                                      end_date: datetime,
                                      traits_source: str = "ent_state"):
    # Add location if missing
    if not eql_model.has_and_entity('location'):
        eql_model.add(MetaLangEntity(type='location', properties=[], negation=False))

    result = []
    for and_query in eql_model.yield_leafs(operator='AND'):

        location_data = await bd_entity_property_adapter.load_expanded_entities_with_eql(
            and_query,
            entity_types=['location'],
            unmatched_entities=unmatched_entities,
            unmatched_traits=unmatched_traits,
            start_date=start_date,
            end_date=end_date,
            traits_source=traits_source,
        )
        if not location_data:
            continue

        locations_by_obs = {}
        for row in location_data.list():
            if not row.get('traits'):
                continue
            traits = json.loads(row['traits']) if isinstance(row['traits'], str) else row['traits']
            locations_by_obs.setdefault(row['observation_id'], []).append(traits)

        if not locations_by_obs:
            continue

        entity_data = await bd_entity_property_adapter.load_expanded_entities_with_eql(
            and_query,
            entity_types=entity_types,
            unmatched_entities=unmatched_entities,
            unmatched_traits=unmatched_traits,
            start_date=start_date,
            end_date=end_date,
            traits_source=traits_source,
        )
        if not entity_data:
            continue

        for row in entity_data.list():
            obs_id = row['observation_id']
            if obs_id not in locations_by_obs:
                continue
            item = dict(row)
            if isinstance(item.get('traits'), str):
                item['traits'] = json.loads(item['traits'])
            item['location'] = locations_by_obs[obs_id]
            result.append(item)

    return result


async def get_located_observation_entities(query: str,
                                           entity_types: List[str],
                                           unmatched_entities: Optional[int] = 0,
                                           unmatched_traits: Optional[int] = 0,
                                           start_date: Optional[datetime] = None,
                                           end_date: Optional[datetime] = None,
                                           traits_source: str = "property_state") -> list:
    if not query.strip():
        return []

    if not entity_types:
        return []

    eql_model = parse_eql(query)

    return await search_observation_location(eql_model, entity_types, unmatched_entities, unmatched_traits,
                                              start_date, end_date, traits_source=traits_source)
