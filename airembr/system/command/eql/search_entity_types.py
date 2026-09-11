from datetime import datetime
from typing import Optional

from airembr.model.system.meta_language.meta_lang_model import MetaLangEntity
from airembr.system.adapter.bigdata.big_data_adapter import bd_entity_property_adapter
from airembr.system.command.eql.errors import parse_eql


async def get_observation_entity_types(query: str,
                                       unmatched_entities: Optional[int] = 0,
                                       unmatched_traits: Optional[int] = 0,
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None,
                                       with_locations: bool = False) -> list:
    if not query.strip():
        return []

    eql_model = parse_eql(query)

    # Add location if missing
    if with_locations and not eql_model.has_and_entity('location'):
        eql_model.add(MetaLangEntity(type='location', properties=[], negation=False))

    counts: dict = {}
    for and_query in eql_model.yield_leafs(operator='AND'):
        data = await bd_entity_property_adapter.load_entity_types_with_eql(
            and_query,
            unmatched_entities,
            unmatched_traits,
            start_date=start_date,
            end_date=end_date
        )
        if data:
            for row in data.list():
                entity_type = row['entity_type']
                counts[entity_type] = counts.get(entity_type, 0) + row['count']

    return [{"id": t, "name": t, "count": c} for t, c in counts.items()]
