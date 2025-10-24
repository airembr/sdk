from typing import List, Tuple, Optional

from sdk.airembr.service.time.time import now_in_utc
from sdk.airembr.transport.flat_fact import FlatFact
from sdk.airembr.transport.flat_relation import FlatRelation
from durable_dot_dict.dotdict import DotDict


def _convert_traits(flat_relation: FlatRelation):
    traits = flat_relation.get(FlatRelation.ENTITY_TRAITS, None)
    if traits:
        _data = DotDict({FlatFact.TRAITS: traits})
        if _data is not None:
            flat_relation[FlatRelation.ENTITY_TRAITS] = _data

    return flat_relation


def convert_to_fact_entities_timers(
        storage_payload: List[List[Tuple[DotDict, FlatRelation, List[DotDict], Optional[DotDict]]]]) -> Tuple[List[DotDict], List[DotDict], List[DotDict]]:
    if not storage_payload:
        return [], [], []

    if isinstance(storage_payload[0], list):
        # Get one list of events
        data = [item for sublist in storage_payload for item in sublist]
    else:
        data = storage_payload

    if len(data) <= 0:
        return [], [], []

    facts = []
    # storage_entities = []
    entities = []
    timers = []

    for row in data:

        if len(row) != 4:
            raise ValueError(f"Incorrect payload {row}. Expected 4 data types.")

        flat_fact, flat_relation, flat_context_entities, flat_timer = row
        if flat_timer:
            timers.append(flat_timer)

        flat_fact[FlatFact.METADATA_TIME_INSERT] = now_in_utc()

        flat_relation = _convert_traits(flat_relation)

        # Save as entity also event
        entities.append(flat_relation)

        # Append only not abstract with ids
        entities.extend(
            [ent for ent in flat_context_entities if ent.get('entity.id', None) is not None]
        )

        # Add to storage
        facts.append(flat_fact)

    return facts, entities, timers