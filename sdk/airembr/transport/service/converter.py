from typing import List, Tuple, Optional

from sdk.airembr.model.fact import Fact, EntityObject, Event, Metadata
from sdk.airembr.service.time.time import now_in_utc
from sdk.airembr.transport.flat_fact import FlatFact
from sdk.airembr.transport.flat_observation_entity import ObservationEntity
from sdk.airembr.transport.flat_relation import FlatRelation
from durable_dot_dict.dotdict import DotDict


def _convert_traits(flat_relation: FlatRelation):
    traits = flat_relation.get(FlatRelation.ENTITY_TRAITS, None)
    if traits:
        _data = DotDict(traits)
        if _data is not None:
            flat_relation[FlatRelation.ENTITY_TRAITS] = _data

    return flat_relation


def _get_entity(fact, object_entities):
    key = (fact[FlatFact.ACTOR_PK], fact[FlatFact.ACTOR_DATA_HASH])
    actor_traits = object_entities.get(key, {})
    return EntityObject(
        id=fact[FlatFact.ACTOR_ID],
        pk=fact[FlatFact.ACTOR_PK],
        type=fact[FlatFact.ACTOR_TYPE],
        data_hash=fact[FlatFact.ACTOR_DATA_HASH],
        traits=actor_traits.get('entity.traits', {})
    )


def _get_context_entity(entity):
    return EntityObject(
        id=entity[ObservationEntity.ENTITY_ID],
        pk=entity[ObservationEntity.ENTITY_PK],
        type=entity[ObservationEntity.ENTITY_TYPE],
        data_hash=entity[ObservationEntity.DATA_HASH],
        traits=entity[ObservationEntity.ENTITY_TRAITS]
    )


def _get_event(fact, event_entities, object_entities):
    event = Event(
        id=fact[FlatFact.REL_ID],
        type=fact[FlatFact.REL_TYPE],
        label=fact[FlatFact.REL_LABEL],
        metadata=Metadata(
            insert=fact[FlatFact.METADATA_TIME_INSERT],
            update=fact.get(FlatFact.METADATA_TIME_UPDATE, None),
            create=fact[FlatFact.METADATA_TIME_CREATE]
        ),
    )
    key = fact.get(FlatFact.REL_ID, None)
    if key:
        relation = event_entities.get(key, None)
        if relation:
            event.traits = relation.get('entity.traits', {})

    if FlatFact.OBJECT_ID in fact:
        key = (fact[FlatFact.OBJECT_PK], fact[FlatFact.OBJECT_DATA_HASH])
        object_traits = object_entities.get(key, {})
        event.object = EntityObject(
            id=fact[FlatFact.OBJECT_ID],
            pk=fact[FlatFact.OBJECT_PK],
            type=fact[FlatFact.OBJECT_TYPE],
            data_hash=fact[FlatFact.OBJECT_DATA_HASH],
            traits=object_traits.get('entity.traits', {})
        )

    return event


def _convert_fact(data):
    facts = []
    object_entities = {}
    event_entities = {}
    context_entities = []
    timers = []

    for row in data:

        if len(row) != 4:
            raise ValueError(f"Incorrect payload {row}. Expected 4 data types.")

        flat_fact, flat_relation, flat_context_entities, flat_timer = row
        if flat_timer:
            timers.append(flat_timer)

        flat_fact[FlatFact.METADATA_TIME_INSERT] = now_in_utc()

        flat_relation = _convert_traits(flat_relation)

        event_entities[flat_relation[FlatRelation.ENTITY_ID]] = flat_relation

        for ent in flat_context_entities:
            # Skip abstract entities
            if ent.get(FlatRelation.ENTITY_ID, None) is None:
                continue

            key = (ent[FlatRelation.ENTITY_PK], ent[FlatRelation.DATA_HASH])

            if key not in object_entities:
                object_entities[key] = ent

        for ent in flat_context_entities:
            context_entities.append(_get_context_entity(ent))

        # Add to storage
        facts.append(flat_fact)

    actor_id_to_fact = {}
    for fact in facts:  # TODO need to be sorted

        actor_key = fact[FlatFact.ACTOR_ID]
        actor = _get_entity(fact, object_entities)

        if actor_key not in actor_id_to_fact:
            f = Fact(
                id=fact[FlatFact.ID],
                actor=actor,
                context=context_entities
            )
        else:
            f = actor_id_to_fact[actor_key]

        # Merge traits and event if needed
        if actor.data_hash != f.actor.data_hash:
            merged = DotDict(f.actor.traits) << DotDict(actor.traits).flat()
            f.actor.traits = merged

        session = fact[FlatFact.SESSION_ID]
        source = fact[FlatFact.SOURCE_ID]
        event = _get_event(fact, event_entities, object_entities)

        f.sessions.add(session)
        f.sources.add(source)
        f.events.append(event)

        actor_id_to_fact[actor_key] = f

    return actor_id_to_fact


from collections import defaultdict


def _group_by_observation_id(data):
    groups = defaultdict(list)

    for tup in data:
        first_obj = tup[0]

        if first_obj is None:
            continue

        obs_id = first_obj['observation.id']

        if obs_id:
            groups[obs_id].append(tup)

    return list(groups.values())


def convert_to_agg_facts(
        storage_payload: List[List[Tuple[DotDict, FlatRelation, List[DotDict], Optional[DotDict]]]]):
    if not storage_payload:
        return

    for group in _group_by_observation_id(storage_payload):
        yield _convert_fact(group)
