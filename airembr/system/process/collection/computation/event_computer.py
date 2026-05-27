import time
from typing import Tuple, List, Optional, Dict, AsyncGenerator, Any
from uuid import uuid4

from durable_dot_dict.dotdict import DotDict

from airembr.system.process.collection.computation.entity_service import index_entities, link_state_entities, \
    compute_data_hashes, get_entity_gids
from airembr.model.bigdata.flat_sys_timer import FlatSysTimer
from airembr.core.data.resolver import resolve_dot_dict_values
from airembr.system.process.logging.log_handler import get_logger
from airembr.model.system.transport_payload import FactTransportPayload
from airembr.core.hash.data_hasher import hash_dict_64
from airembr.core.hash.hash import md5
from airembr.system.utils.text.formaters import _stringify_dict
from airembr_sdk.core.date import now_in_utc
from airembr.core.entity.getters import get_entity_id
from airembr_sdk.core.entity.identification import generate_pk, generate_triplet_id, generate_hid
from airembr.model.bigdata.flat_ent_history import FlatEntityHistory
from airembr.model.bigdata.flat_fact import FlatFact
from airembr.model.bigdata.flat_observation_entity import ObservationEntity
from airembr.model.bigdata.flat_relation import FlatRelation
from airembr_sdk.model.core.instance_link import InstanceLink
from airembr.model.api.request.observation import Observation, ObservationRelation
from airembr.model.system.headers import Headers

logger = get_logger(__name__)


def _get_status_int(status):
    if status == 'on':
        return 1
    elif status == 'off':
        return 0
    return 2


def _get_rel(observation: Observation, relation: ObservationRelation, now) -> FlatRelation:
    flat_relation = FlatRelation()
    observer: ObservationEntity = observation.get_observer()
    if relation.traits:
        traits = resolve_dot_dict_values(
            relation.traits,
            DotDict({
                # Index entities
                "entities": observation.entities.index()
            }))
    else:
        traits = {}

    if relation.type:
        traits['$type'] = relation.type
    if relation.label:
        traits['$label'] = relation.label

    entity_type = 'event'
    data_hash = hash_dict_64(traits)
    flat_relation[FlatRelation.ENTITY_TRAITS] = traits
    flat_relation[FlatRelation.ENTITY_TRAITS_TEXT] = _stringify_dict(traits)
    flat_relation[FlatRelation.DATA_HASH] = data_hash
    fields = sorted(DotDict(traits).flat())
    flat_relation[FlatRelation.SCHEMA_HASH] = hash_dict_64(fields)
    # flat_relation[FlatRelation.FIELD_HASH] = [hash_dict_64(field) for field in fields]

    flat_relation[FlatRelation.REL_TYPE] = relation.type
    flat_relation[FlatRelation.REL_LABEL] = relation.label

    flat_relation[FlatRelation.TS] = now

    flat_relation[FlatRelation.ENTITY_TYPE] = entity_type
    # Here is the key question how to identify event entity. Do we create alway new event entity ot
    # the event entity is the same if it has the save type, event_type, and data.
    # Now we use ID as: event entity is the same if it has the save type, event_type, and data
    if True:
        type_id = f"{entity_type}-{relation.label if relation.label else relation.type}"
        _gen_rel_pk = generate_pk(type_id, data_hash)
        flat_relation[FlatRelation.ENTITY_PK] = _gen_rel_pk
        flat_relation[FlatRelation.ENTITY_ID] = _gen_rel_pk
    else:
        flat_relation[FlatRelation.ENTITY_ID] = relation.id
        flat_relation[FlatRelation.ENTITY_PK] = generate_pk(entity_type, relation.id)

    flat_relation[FlatRelation.ENTITY_HID] = generate_hid(flat_relation[FlatRelation.ENTITY_PK],
                                                          flat_relation[FlatRelation.DATA_HASH])
    flat_relation[FlatRelation.OBS_ID] = observation.id
    flat_relation[FlatRelation.CONTEXT] = entity_type
    flat_relation[FlatRelation.CONSENTS_GRANTED] = observation.get_consents()

    # Must be last
    flat_relation[FlatRelation._OBSERVER_ID] = observer.instance.id
    flat_relation[FlatRelation.OBSERVER_PK] = observer.instance.generate_pk()

    return flat_relation


def append_relation_to_context_entities(entities_by_ref: Dict[str, DotDict], relation: ObservationRelation) -> List[
    DotDict]:
    storage_context_entities = []

    # Add relation as entity

    for _, observation_entity in entities_by_ref.items():
        try:

            # Add to entities new data
            observation_entity[FlatEntityHistory.CONTEXT] = 'entity'
            observation_entity[FlatEntityHistory.REL_TYPE] = relation.type
            observation_entity[FlatEntityHistory.REL_LABEL] = relation.label
            observation_entity[FlatEntityHistory.TIME_CREATE] = relation.ts

            storage_context_entities.append(observation_entity)
        except ValueError as e:
            logger.error(e)

    return storage_context_entities


def _get_actor_in_entities(entities_by_ref: Dict[str, Any], observed_rel) -> Tuple[
    Optional[InstanceLink], Optional[DotDict]]:
    actor_link = observed_rel.get_actor()
    if actor_link:
        return actor_link, entities_by_ref.get(actor_link.link, None)
    return actor_link, None


def _ms_in_hour():
    t = time.time()
    return int(((t % 3600) * 1000) * 1000)


# def _generate_fact_immutable_id(flat_fact: FlatFact):
#     unique_data = {
#         "observer": flat_fact.get_or_none('observer'),
#         "actor": flat_fact.get_or_none('actor'),
#         "object": flat_fact.get_or_none('object'),
#         "relation": {
#             "label": flat_fact.get_or_none(FlatFact.LABEL),
#             "type": flat_fact.get_or_none(FlatFact.TYPE),
#             "data_hash": flat_fact.get_or_none(FlatFact.REL_DATA_HASH),
#         },
#         "observation": flat_fact.get_or_none(FlatFact.OBS_ID),
#         "source": flat_fact.get_or_none(FlatFact.SOURCE_ID),
#         "session": flat_fact.get_or_none(FlatFact.SESSION_ID),
#         "semantic": (flat_fact.get_or_none(FlatFact.SEMANTIC_SUMMARY),
#                      flat_fact.get_or_none(FlatFact.SEMANTIC_DESCRIPTION))
#     }
#     hash_base  = DotDict(unique_data).flat()
#     hash_base_json = orjson.dumps(
#         hash_base,
#         option=orjson.OPT_SORT_KEYS
#     )
#     return md5(hash_base_json)

def _create_fact(observation: Observation,
                 relation: ObservationRelation,
                 observer: DotDict,
                 observer_link: InstanceLink,
                 actor: DotDict,
                 actor_link: Optional[InstanceLink],
                 object: Optional[ObservationEntity],
                 object_link: Optional[InstanceLink],
                 flat_relation: FlatRelation,
                 storage_context_entities: List) -> FlatFact:
    order = _ms_in_hour()

    flat_fact = FlatFact({
        FlatFact.ID: str(uuid4()),  # Unique id of record (hyper edge id)
        FlatFact.LABEL: relation.label,
        FlatFact.TYPE: relation.type,
    }) << {
                    FlatFact.SOURCE_ID: get_entity_id(observation.source),
                    FlatFact.SESSION_ID: observation.get_session_id(),
                    FlatFact.OBS_ID: observation.id,
                    FlatFact.OBS_LABEL: observation.label.lower() if observation.label else 'observation',

                    FlatFact.METADATA_TIME_CREATE: relation.ts,
                    FlatFact.METADATA_TIME_INSERT: now_in_utc(),
                    FlatFact.METADATA_ORDER: order,

                    FlatFact.TAGS: relation.tags,
                    FlatFact.METADATA_CONTEXT_COUNT: len(storage_context_entities),
                    FlatFact.METADATA_CONTEXT_ENTITIES: [ctx[ObservationEntity.ENTITY_TYPE] for ctx in
                                                         storage_context_entities],
                    FlatFact.CONSENTS_GRANTED: observation.get_consents(),
                }

    # Observer data
    flat_fact << {
        FlatFact.OBSERVER_ID: observer[FlatEntityHistory.ENTITY_ID],
        FlatFact.OBSERVER_PK: observer[FlatEntityHistory.ENTITY_PK],
        FlatFact.OBSERVER_TYPE: observer[FlatEntityHistory.ENTITY_TYPE],
        FlatFact.OBSERVER_ROLE: observer_link.role,
        FlatFact.OBSERVER_DATA_HASH: observer.get_or_none(FlatEntityHistory.DATA_HASH),
        FlatFact.OBSERVER_SCHEMA_HASH: observer.get_or_none(FlatEntityHistory.SCHEMA_HASH)
    }

    if flat_relation:
        # Link to relation
        actor_pk = actor.get(FlatEntityHistory.ENTITY_PK, None) if actor else None
        object_pk = object.get(FlatEntityHistory.ENTITY_PK, None) if object else None
        rel_id = flat_relation.get(FlatRelation.ENTITY_ID)
        rel_pk = flat_relation.get(FlatRelation.ENTITY_PK)

        flat_fact << {
            FlatFact.REL_ID: rel_id,
            FlatFact.REL_PK: rel_pk,
            FlatFact.REL_HID: flat_relation.get(FlatRelation.ENTITY_HID, None),
            FlatFact.REL_TID: generate_triplet_id(actor_pk, relation.label, object_pk),
            FlatFact.REL_LABEL: relation.label,  # eg. viewed
            FlatFact.REL_TYPE: relation.type,  # eg. event
            FlatFact.REL_DATA_HASH: flat_relation.get(FlatRelation.DATA_HASH, None),
            FlatFact.REL_SCHEMA_HASH: flat_relation.get(FlatRelation.SCHEMA_HASH, None),
            FlatFact.SUBJECTIVE: relation.subjective
        }

    if actor:
        # This is the FK to actor
        flat_fact[FlatFact.ACTOR_PK] = actor[FlatEntityHistory.ENTITY_PK]
        flat_fact[FlatFact.ACTOR_ID] = actor[FlatEntityHistory.ENTITY_ID]
        flat_fact[FlatFact.ACTOR_HID] = actor[FlatEntityHistory.ENTITY_HID]
        flat_fact[FlatFact.ACTOR_IID] = actor[FlatEntityHistory.ENTITY_IID]
        flat_fact[FlatFact.ACTOR_IID_TYPE] = actor[FlatEntityHistory.ENTITY_IID_TYPE]
        flat_fact[FlatFact.ACTOR_TYPE] = actor[FlatEntityHistory.ENTITY_TYPE]
        flat_fact[FlatFact.ACTOR_ROLE] = actor_link.role
        flat_fact[FlatFact.ACTOR_LABEL] = actor[FlatEntityHistory.ENTITY_LABEL]
        flat_fact[FlatFact.ACTOR_DATA_HASH] = actor.get_or_none(FlatEntityHistory.DATA_HASH)
        flat_fact[FlatFact.ACTOR_SCHEMA_HASH] = actor.get_or_none(FlatEntityHistory.SCHEMA_HASH)
        # Is A
        flat_fact[FlatFact.ACTOR_IS_A_ID] = actor[FlatEntityHistory.IS_A_ID]
        flat_fact[FlatFact.ACTOR_IS_A_KIND] = actor[FlatEntityHistory.IS_A_KIND]
        # Part of
        flat_fact[FlatFact.ACTOR_PART_OF_ID] = actor[FlatEntityHistory.PART_OF_ID]
        flat_fact[FlatFact.ACTOR_PART_OF_KIND] = actor[FlatEntityHistory.PART_OF_KIND]
    elif actor_link:
        flat_fact[FlatFact.ACTOR_TYPE] = actor_link.link  # Link is type in abstract entities
        flat_fact[FlatFact.ACTOR_ROLE] = actor_link.role

    if object:
        # This is the FK to object
        flat_fact[FlatFact.OBJECT_PK] = object[FlatEntityHistory.ENTITY_PK]
        flat_fact[FlatFact.OBJECT_ID] = object[FlatEntityHistory.ENTITY_ID]
        flat_fact[FlatFact.OBJECT_HID] = object[FlatEntityHistory.ENTITY_HID]
        flat_fact[FlatFact.OBJECT_IID] = object[FlatEntityHistory.ENTITY_IID]
        flat_fact[FlatFact.OBJECT_IID_TYPE] = object[FlatEntityHistory.ENTITY_IID_TYPE]
        flat_fact[FlatFact.OBJECT_TYPE] = object[FlatEntityHistory.ENTITY_TYPE]
        flat_fact[FlatFact.OBJECT_LABEL] = object[FlatEntityHistory.ENTITY_LABEL]
        flat_fact[FlatFact.OBJECT_DATA_HASH] = object.get_or_none(FlatEntityHistory.DATA_HASH)
        flat_fact[FlatFact.OBJECT_SCHEMA_HASH] = object.get_or_none(FlatEntityHistory.SCHEMA_HASH)
        if object_link:
            flat_fact[FlatFact.OBJECT_ROLE] = object_link.role
        # Is A
        flat_fact[FlatFact.OBJECT_IS_A_ID] = object[FlatEntityHistory.IS_A_ID]
        flat_fact[FlatFact.OBJECT_IS_A_KIND] = object[FlatEntityHistory.IS_A_KIND]
        # Part of
        flat_fact[FlatFact.OBJECT_PART_OF_ID] = object[FlatEntityHistory.PART_OF_ID]
        flat_fact[FlatFact.OBJECT_PART_OF_KIND] = object[FlatEntityHistory.PART_OF_KIND]
    elif object_link:
        flat_fact[FlatFact.OBJECT_TYPE] = object_link.link  # Link is type in abstract entities
        flat_fact[FlatFact.OBJECT_ROLE] = object_link.role

    if relation.has_sematic_part():
        _summary, _description = relation.text.render(actor_link,
                                                      object_link,
                                                      observation)

        flat_fact[FlatFact.SEMANTIC_DESCRIPTION] = _description
        flat_fact[FlatFact.SEMANTIC_SUMMARY] = _summary
        flat_fact[FlatFact.SEMANTIC_NER] = relation.text.ner

        if relation.text.summary:
            flat_fact[FlatFact.TEXT_SSID] = md5(relation.text.summary)
        if relation.text.description:
            flat_fact[FlatFact.TEXT_SDID] = md5(relation.text.description)

    return flat_fact


def _create_timer(observation, actor, object, observed_rel, flat_fact, now) -> Optional[DotDict]:
    if not observed_rel.timer:
        return None
    timer = DotDict()
    flat_fact[FlatFact.SYS_TIMER_ID] = observed_rel.timer.id
    flat_fact[FlatFact.SYS_TIMER_STATUS] = _get_status_int(observed_rel.timer.status.value)

    timer[FlatSysTimer.ID] = observed_rel.timer.id
    timer[FlatSysTimer.TS] = now
    timer[FlatSysTimer.STATUS] = _get_status_int(observed_rel.timer.status.value)
    timer[FlatSysTimer.TIMEOUT] = observed_rel.timer.timeout
    timer[FlatSysTimer.EVENT] = observed_rel.timer.event
    timer[FlatSysTimer.SOURCE_ID] = flat_fact[FlatFact.SOURCE_ID]
    timer[FlatSysTimer.OBS_ID] = observation.id
    timer[FlatSysTimer.OBS_LABEL] = flat_fact[FlatFact.OBS_LABEL]
    timer[FlatSysTimer.TRAITS] = flat_fact.get(FlatFact.TRAITS, {})
    if actor:
        timer[FlatSysTimer.ACTOR_ID] = actor[FlatEntityHistory.ENTITY_ID]
        timer[FlatSysTimer.ACTOR_TYPE] = actor[FlatEntityHistory.ENTITY_TYPE]
        timer[FlatSysTimer.ACTOR_DATA_HASH] = actor[FlatEntityHistory.DATA_HASH]
        timer[FlatSysTimer.OBJECT_ROLE] = actor[ObservationEntity.ENTITY_ROLE]

    if object:
        timer[FlatSysTimer.OBJECT_ID] = object[FlatEntityHistory.ENTITY_ID]
        timer[FlatSysTimer.OBJECT_TYPE] = object[FlatEntityHistory.ENTITY_TYPE]
        timer[FlatSysTimer.OBJECT_DATA_HASH] = object[FlatEntityHistory.DATA_HASH]
        timer[FlatSysTimer.OBJECT_ROLE] = object[ObservationEntity.ENTITY_ROLE]

    return timer


async def compute_events(observation: Observation, headers: Headers) -> AsyncGenerator[
    FactTransportPayload, None]:
    # Get Entities, each has data_hash
    _entities_by_ref = index_entities(observation)

    # Get global entity ids
    _entity_gids = get_entity_gids(_entities_by_ref)

    # Link state
    _entities_by_ref = link_state_entities(_entities_by_ref)

    # Now we are ready to compute data hashed, all traits are there
    _entities_by_ref = compute_data_hashes(_entities_by_ref)

    # Check observer in observation (should be in entities)
    observer_link = observation.observer
    observer: Optional[DotDict] = _entities_by_ref.get(observer_link.link, None)

    if not observer:  # no observer in entities
        logger.error(
            f"Observer `{observer_link}` not available in entities for {observation.id}. This should not be possible if observation validation is in place.")

    else:
        now = now_in_utc()

        if not observation.relation:
            # No facts
            for ent in _entities_by_ref.values():
                ent[FlatEntityHistory.CONTEXT] = 'observation'

            yield FactTransportPayload(
                source_id=observation.source.id,
                observation={
                    "id": observation.id,
                    "observer": observer.get_or_none(FlatEntityHistory.ENTITY_PK),
                    "text": {
                        "summary": observation.text.summary,
                        "description": observation.text.description,
                        "ner": observation.text.ner
                    },
                    "label": observation.label,
                    "traits": observation.traits
                },
                fact={},
                relation={},
                entities=list(_entities_by_ref.values()),
                timer=None,
                gids=_entity_gids,
                trace_id=headers.get_trace_id(),
                session=observation.session.model_dump(exclude_none=True)
            )
        else:
            # Get relation
            for relation in observation.relation:

                flat_relation = _get_rel(observation, relation, now)

                # Get all entities (appends event)
                storage_context_entities = append_relation_to_context_entities(_entities_by_ref, relation)

                # Get actor

                actor_link, actor = _get_actor_in_entities(_entities_by_ref, relation)

                # Get objects

                object_links = list(relation.get_objects())
                if object_links:
                    for object_link in object_links:
                        object = _entities_by_ref.get(object_link.link, None)

                        # Get fact
                        flat_fact = _create_fact(observation,
                                                 relation,
                                                 observer,
                                                 observer_link,
                                                 actor,
                                                 actor_link,
                                                 object,
                                                 object_link,
                                                 flat_relation,
                                                 storage_context_entities)

                        timer = _create_timer(observation, actor, object, relation, flat_fact, now)

                        yield FactTransportPayload(
                            source_id=observation.source.id,
                            observation={
                                "id": observation.id,
                                "observer": observer.get_or_none(FlatEntityHistory.ENTITY_PK),
                                "text": {
                                    "summary": observation.text.summary,
                                    "description": observation.text.description,
                                    "ner": observation.text.ner
                                },                                "label": observation.label,
                                "traits": observation.traits
                            },
                            fact=flat_fact.to_dict(),
                            relation=flat_relation.to_dict(),
                            entities=storage_context_entities,
                            timer=timer,
                            gids=_entity_gids,
                            trace_id=headers.get_trace_id(),
                            session=observation.session.model_dump(exclude_none=True)
                        )
                else:
                    flat_fact = _create_fact(observation,
                                             relation,
                                             observer,
                                             observer_link,
                                             actor,
                                             actor_link,
                                             None,
                                             None,
                                             flat_relation,
                                             storage_context_entities)

                    timer = _create_timer(observation, actor, None, relation, flat_fact, now)

                    yield FactTransportPayload(
                        source_id=observation.source.id,
                        observation={
                            "id": observation.id,
                            "observer": observer.get_or_none(FlatEntityHistory.ENTITY_PK),
                            "text": {
                                "summary": observation.text.summary,
                                "description": observation.text.description,
                                "ner": observation.text.ner
                            },                            "label": observation.label,
                            "traits": observation.traits
                        },
                        fact=flat_fact.to_dict(),
                        relation=flat_relation.to_dict(),
                        entities=storage_context_entities,
                        timer=timer,
                        gids=_entity_gids,
                        trace_id=headers.get_trace_id(),
                        session=observation.session.model_dump(exclude_none=True)
                    )
