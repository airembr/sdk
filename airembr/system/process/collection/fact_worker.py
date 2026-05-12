from time import time

from typing import List, Optional, Dict, Tuple, Set

from durable_dot_dict.dotdict import DotDict

from pararun.consumer.batcher import BulkedResult
from pararun.model.batcher import BatcherConfig
from pararun.model.transport_context import TransportContext, RECORDS
from pararun.publisher.deferer import deferred_execution
from pararun_adapter import queue_type

from airembr.core.entity.identification import generate_pk, generate_hid
from airembr.core.hash.hash import md5
from airembr.core.time.profiler import time_profiler
from airembr.core.data.bigint import bigint_to_unsigned_hex
from airembr.core.hash.data_hasher import hash_dict_64
from airembr.system.utils.text.formaters import _stringify_dict
from airembr.system.service.bigdata.entity_transformer import compute_entity_property_from_entities
from airembr.system.service.bigdata.observation_converter import get_obs_2_entity_object, get_rel_2_entity_object
from airembr.system.logging.log_handler import get_logger, log_handler
from airembr.model.system.transport_payload import FactTransportPayload
from airembr.model.bigdata.flat_ent_2_obs import FlatEntity2Observation
from airembr.model.bigdata.flat_obs_2_entity import FlatObs2Entity
from airembr.model.bigdata.flat_text import FlatText
from airembr.model.bigdata.flat_fact import FlatFact
from airembr.model.bigdata.flat_relation import FlatRelation
from airembr.model.system.job_tags import FACT_STORAGE_TAG, ENTITY_PROPERTY_TAG
from airembr.model.bigdata.flat_observation_entity import ObservationEntity
from airembr.model.bigdata.flat_ent_history import FlatEntityHistory
from airembr.model.system.context import Context, ServerContext, get_context
from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping, entity_history_mapping, \
    sys_timer_mapping, entity_property, observation_2_entity_mapping, sys_ent_2_obs, \
    sys_ent_2_gid, sys_text_mapping
from airembr.system.config.global_config import global_settings
from airembr.system.adapter.bigdata.tool.column_mapper import map_to_table_columns
from airembr.system.logging import extra_info
from airembr.system.adapter.bigdata.big_data_adapter import *
from airembr.system.config.sys_config import sys_config
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.sdk.common.date import now_in_utc
from airembr.system.process.collection.reshaping.traits_reshaper import reshape_event
from airembr.system.process.collection.validation.event_validation import validate_event
from airembr.system.process.collection.entity_properties_worker import save_properties_batch, entity_properties_worker
from airembr.system.process.collection.caching.actor_cache import has_cache, delete_cache_node, set_cache

logger = get_logger(__name__)
_evt_mapping = event_mapping()
_ent_history_mapping = entity_history_mapping()
_ent_property_mapping = entity_property()
_sys_timer_mapping = sys_timer_mapping()
_sys_obs_2_entity_mapping = observation_2_entity_mapping()
_sys_ent_2_obs_map = sys_ent_2_obs()
_sys_ent_2_gid_map = sys_ent_2_gid()
_sys_text_mapping = sys_text_mapping()

CACHE_PREFIX = "entity"

async def _validate_and_reshape(entity_type: str, event_id: str, event_type: str, data: DotDict):
    valid = True

    # Event Validation
    validation = None
    if sys_config.enable_event_validation:
        validation = await validate_event(event_type, data)
        valid = not validation.error

        # Register if not valid
        if not validation.is_valid():
            logger.warning(
                validation.message[:4092],
                extra=extra_info.exact(
                    origin='Event Validation',
                    error_number="E-0005",
                    flow_id=None,
                    node_id=None,
                    event_id=event_id,
                    entity_id=None,
                    package=__name__,
                    traceback=validation.trace
                )
            )

    # Event Reshaping
    if sys_config.enable_event_reshaping:

        # Reshape only if valid
        if validation and validation.is_valid():
            # Reshape valid events
            data = await reshape_event(entity_type, event_id, event_type, data)

    # # Anonymize. Event data compliance
    # if sys_config.enable_data_compliance:
    #     event_entity_id = flat_event.get(FlatEvent.ENTITY_ID, None)
    #     if event_entity_id is not None:
    #         # Profile must have set consents to know when to anonymize data
    #         properties = await anon_event_payload_properties(
    #             event_entity_id,
    #             profile_consents,
    #             flat_event
    #         )

    return data, valid


async def _validate_relation(flat_fact, flat_relation: FlatRelation) -> FlatRelation:
    traits = flat_relation.get(FlatRelation.ENTITY_TRAITS, None)
    if traits:
        actor_type = flat_fact | FlatFact.ACTOR_TYPE
        fact_type = flat_fact | FlatFact.TYPE
        fact_id = flat_fact | FlatFact.ID
        # TODO currently validates and reshapes only event traits
        # TODO Could add actor and object
        # Separate traits
        _data = DotDict({FlatFact.TRAITS: traits})
        _data, valid = await _validate_and_reshape(
            entity_type=actor_type,
            event_id=fact_id,
            event_type=fact_type,
            data=_data)
        if _data is not None:
            # Get data from traits
            flat_relation[FlatRelation.ENTITY_TRAITS] = _data[FlatFact.TRAITS]

    return flat_relation


async def _validate_fact(flat_fact: FlatFact) -> FlatFact:
    valid = True

    if flat_fact is not None:
        if flat_fact.get(FlatFact.METADATA, None) is None:
            flat_fact[FlatFact.METADATA] = {"valid": valid}
        else:
            flat_fact[FlatFact.METADATA_VALID] = valid

    return flat_fact


async def _save_properties(transport_context: TransportContext, storage_context_entities, queue: bool):
    property_rows = list(compute_entity_property_from_entities(storage_context_entities))

    if not queue:
        await save_properties_batch(transport_context, property_rows)

    else:
        status = await entity_properties_worker(transport_context, property_rows)
        if status.logs:
            log_handler.add(status.logs)

        if status.error:
            raise status.error


async def _save_entity_gids(context, entity_gids):
    if entity_gids:
        start = time()

        # Convert to rows
        gid_rows = map_to_table_columns(entity_gids,
                                        mapping=_sys_ent_2_gid_map)

        # Save
        status, total_rows, saved_rows, message = await bd_event_adapter.adapter.stream(gid_rows,
                                                                                        _sys_ent_2_gid_map)

        end_time = time()
        logger.info(
            f"Entity Global Identifiers: Saved {saved_rows}, "
            f"Time={end_time - start}, "
            f"Context={context.tenant}/{context.production}")


async def _save_facts(transport_context, storage_facts):
    if storage_facts:
        start_time = time()

        # Save events
        _event_rows = map_to_table_columns(storage_facts, mapping=_evt_mapping)

        status, total_rows, saved_rows, message = await bd_event_adapter.adapter.stream(_event_rows,
                                                                                        _evt_mapping)

        end_time = time()

        logger.stat(
            f"Events: Saved {saved_rows}, "
            f"Time={end_time - start_time} (Saving={end_time - start_time}), Context={transport_context.tenant}/{transport_context.production}")


async def _save_texts(context, texts: Set[Tuple[str, str, bool]], relation: Optional[FlatRelation], source_id: str):
    if texts:
        start = time()
        now = now_in_utc()
        sys_text = [{
            FlatText.ID: md5(text),
            FlatText.SOURCE_ID: source_id,
            FlatText.OBSERVATION_ID: observation_id,
            FlatText.REL_LABEL: relation[FlatRelation.REL_LABEL] if relation else None,
            FlatText.REL_TYPE: relation[FlatRelation.REL_TYPE] if relation else None,
            FlatText.DESCRIPTION: text,
            FlatText.TAGS: [],
            FlatText.ORIGIN: origin,
            FlatText.REQUIRE_NER: ner,
            FlatText.TS: now
        } for text, origin, ner, observation_id in texts]
        text_rows = map_to_table_columns(sys_text, mapping=_sys_text_mapping)
        # Save
        status, total_rows, saved_rows, message = await bd_event_adapter.adapter.stream(text_rows,
                                                                                        _sys_text_mapping)

        end_time = time()
        logger.stat(
            f"Semantics: Saved {saved_rows}, "
            f"Time={end_time - start}, "
            f"Context={context.tenant}/{context.production}")


async def _save_entity_history(context, storage_context_entities):
    # Save Entity History
    start_time = time()

    context_entity_rows = map_to_table_columns(storage_context_entities,
                                               mapping=_ent_history_mapping)

    status, total_rows, saved_rows, message = await bd_event_adapter.adapter.stream(context_entity_rows,
                                                                                    _ent_history_mapping)

    end_time = time()

    logger.stat(
        f"Entity History: Saved {saved_rows}, "
        f"Saving={end_time - start_time}, Context={context.tenant}/{context.production}")


async def _save_ent_2_obs(row_objects) -> tuple:
    obs_2_entity_rows = list(map_to_table_columns(row_objects, mapping=_sys_ent_2_obs_map))
    # Return status, total_rows, saved_rows, message
    return await bd_event_adapter.adapter.stream(obs_2_entity_rows, _sys_ent_2_obs_map)


async def _save_obs_2_entity(row_objects) -> tuple:
    obs_2_entity_rows = list(map_to_table_columns(row_objects, mapping=_sys_obs_2_entity_mapping))
    # Return status, total_rows, saved_rows, message
    return await bd_event_adapter.adapter.stream(obs_2_entity_rows, _sys_obs_2_entity_mapping)


async def _save_timers(context, storage_timers):
    start_time = time()
    timer_rows = map_to_table_columns(storage_timers, mapping=_sys_timer_mapping)

    status, total_rows, saved_rows, message = await bd_event_adapter.adapter.stream(timer_rows,
                                                                                    _sys_timer_mapping)
    end_time = time()
    logger.info(
        f"Timers: Saved {saved_rows}, "
        f"Saving={end_time - start_time}, Context={context.tenant}/{context.production}")


def _get_key(entity_type, entity_id, entity_hash) -> str:
    if entity_hash is None:
        entity_data_hash = '0'
    else:
        entity_data_hash = bigint_to_unsigned_hex(entity_hash)  # Convert for key

    return f"{entity_type}:{entity_id}:{entity_data_hash}"


def _get_key_namespace(entity_type, entity_id):
    return f"{entity_type}:{entity_id}:*"


def _is_already_created(type: str, entity):
    entity_id = entity.get(ObservationEntity.ENTITY_ID, None)
    entity_type = entity.get(ObservationEntity.ENTITY_TYPE, 'unknown')
    entity_hash = entity.get(ObservationEntity.DATA_HASH, None)

    key = _get_key(entity_type, entity_id, entity_hash)

    return has_cache(type, key)


def _update_cached_entities(storage_context_entities, ttl):
    for entity in storage_context_entities:

        # Events are not cached, event is always new, with new id
        if entity.get(FlatEntityHistory.ENTITY_TYPE, None) == 'event':
            continue

        # Delete
        entity_id = entity.get(ObservationEntity.ENTITY_ID, None)
        entity_type = entity.get(ObservationEntity.ENTITY_TYPE, 'unknown')

        delete_cache_node(CACHE_PREFIX, _get_key_namespace(entity_type, entity_id))

        # Update
        entity_hash = entity.get(ObservationEntity.DATA_HASH, None)
        key = _get_key(entity_type, entity_id, entity_hash)

        set_cache(CACHE_PREFIX, key, ttl)


def _yield_not_saved_entities(storage_context_entities):
    for entity in storage_context_entities:
        # Events are not cached, event is always new, with new id
        if entity.get(FlatEntityHistory.ENTITY_TYPE, None) == 'event':
            # We need to swap times (event holds create time in TS)
            entity[FlatEntityHistory.TIME_CREATE] = entity.get(FlatEntityHistory.TS, None)
            entity[FlatEntityHistory.TS] = now_in_utc()
            yield entity
        # Check if an entity is already created
        else:
            # Caching is disabled
            if False and global_settings.entity_cache_ttl > 0:
                # Check cache
                if not _is_already_created(CACHE_PREFIX, entity):  # Keep for 1h
                    yield entity
            else:
                yield entity


async def _store_ent_2_obs(transport_context, obs_2_entity):
    if obs_2_entity:
        # This mapping may not be needed
        ent_2_obs_rows = [
            DotDict() << {
                FlatEntity2Observation.ENTITY_PK: item[FlatObs2Entity.ENTITY_PK],
                FlatEntity2Observation.ENTITY_TYPE: item[FlatObs2Entity.ENTITY_TYPE],
                FlatEntity2Observation.OBSERVATION_ID: item[FlatObs2Entity.OBSERVATION_ID]
            }
            for item in obs_2_entity
        ]

        with time_profiler() as timer:
            status, total_rows, saved_rows, message = await _save_ent_2_obs(ent_2_obs_rows)

        logger.stat(
            f"Entities To Observation: {saved_rows}, "
            f"Saving={timer.duration}, Context={transport_context.tenant}/{transport_context.production}")


async def _store_obs_2_entity(transport_context, obs_2_entity):
    if obs_2_entity:
        with time_profiler() as timer:
            status, total_rows, saved_rows, message = await _save_obs_2_entity(obs_2_entity)
        logger.stat(
            f"Observation to Entity Changes: {saved_rows}, "
            f"Saving={timer.duration}, Context={transport_context.tenant}/{transport_context.production}")


def _get_context_entities(storage_payload):
    if storage_payload.context:
        return [ObservationEntity(item) for item in storage_payload.context]
    return []


def _get_relation(storage_payload, session_id) -> FlatRelation:
    flat_relation = FlatRelation(storage_payload.relation)
    flat_relation[FlatRelation.ENTITY_CLASSIFICATION] = 'entity > occurrent'
    flat_relation[FlatRelation.SESSION_ID] = session_id
    return flat_relation


async def save_events_in_queue(transport_context: TransportContext,
                               batch: List[dict],
                               metadata: Optional[List[dict]] = None,
                               queue=True):
    # Batch has the same type as none batched data but has all rows
    logger.debug(f"Triggered batched processing with {len(batch)} events")

    now = now_in_utc()
    with ServerContext(Context(**transport_context.as_context())) as server_context:

        # Loads all defined entities (all types/classes of entities)

        if len(batch) > 0:

            storage_facts: List[FlatFact] = []
            indexed_entities_by_id: Dict[tuple, DotDict | FlatRelation] = {}
            storage_timers = []
            obs_2_entity = []
            sys_texts = set()

            for fact_transport_payload in batch:

                if not isinstance(fact_transport_payload, dict):
                    raise ValueError(
                        f"Incorrect payload {fact_transport_payload}. Expected dict in schema of FactTransportPayload type, got `{type(fact_transport_payload)}`.")

                # Recreate from dict
                fact_transport_payload = FactTransportPayload(**fact_transport_payload)


                if fact_transport_payload.trace_id:
                    logger.q_info(
                        f"Acquired storage message [{fact_transport_payload.trace_id}] in bulk [{server_context.context.trace_id}]")

                session_id = fact_transport_payload.session.get('id', None) if fact_transport_payload.session else None

                # Index observation
                with time_profiler("Observation indexing"):
                    observation_id = fact_transport_payload.observation.get('id')
                    observer_pk = fact_transport_payload.observation.get('observer', None)
                    observation_traits = fact_transport_payload.observation.get('traits', {})
                    observation_fields = sorted(DotDict(observation_traits).flat())
                    observation_entity_type = 'observation'
                    observation_label = fact_transport_payload.observation.get('label', None)
                    observation_data_hash = hash_dict_64(observation_traits)
                    observation_pk = generate_pk(observation_entity_type, observation_id)
                    observation_entity = {
                        FlatEntityHistory.OBS_ID: observation_id,
                        FlatEntityHistory.SESSION_ID: session_id,
                        FlatEntityHistory.OBSERVER_PK: observer_pk,
                        FlatEntityHistory.ENTITY_ID: observation_id,
                        FlatEntityHistory.ENTITY_HID: generate_hid(observation_pk, observation_data_hash),
                        FlatEntityHistory.ENTITY_PK: observation_pk,
                        FlatEntityHistory.ENTITY_TYPE: observation_entity_type,
                        FlatEntityHistory.ENTITY_CLASSIFICATION: 'entity > occurrent',
                        FlatEntityHistory.ENTITY_LABEL: observation_label,
                        FlatEntityHistory.ENTITY_TRAITS: observation_traits,
                        FlatEntityHistory.ENTITY_TRAITS_TEXT: _stringify_dict(observation_traits),
                        FlatEntityHistory.DATA_HASH: observation_data_hash,
                        FlatEntityHistory.SCHEMA_HASH: hash_dict_64(observation_fields),
                        FlatEntityHistory.FIELD_HASH: [hash_dict_64(field) for field in observation_fields],
                        FlatEntityHistory.REL_TYPE: 'observation',
                        FlatEntityHistory.REL_LABEL: observation_label.lower().replace(' ',
                                                                                       '-') if observation_label else 'observation',
                        FlatEntityHistory.TIME_CREATE: now,

                        FlatEntityHistory.TS: now,
                        FlatEntityHistory.CONTEXT: observation_entity_type,
                    }
                    observation_entity = DotDict() << observation_entity
                    indexed_entities_by_id[(observation_id, observation_data_hash)] = observation_entity

                    # Include observatio as an entity in obs_2_ent
                    obs_2_entity.append(get_obs_2_entity_object(
                        observation_id,
                        observation_entity,
                        session_id=session_id
                    ))

                with time_profiler("Timer indexing"):
                    # Timer
                    if fact_transport_payload.timer:
                        flat_timer = DotDict(fact_transport_payload.timer)
                        storage_timers.append(flat_timer)

                with time_profiler("Text indexing"):

                    # Add fact text + origon to sys_text
                    if fact_transport_payload.description:
                        sys_texts.add(
                            (
                                fact_transport_payload.description,
                                'fact',
                                fact_transport_payload.ner,
                                observation_id
                            )
                        )

                    if fact_transport_payload.summary:
                        sys_texts.add(
                            (
                                fact_transport_payload.summary,
                                'fact',
                                fact_transport_payload.ner,
                                observation_id
                            )
                        )

                    # Add observation text + origin to sys_text
                    obs_text = fact_transport_payload.observation.get('text', None)
                    if obs_text: sys_texts.add(
                        (
                            obs_text,
                            'observation',
                            fact_transport_payload.observation.get('ner', False),
                            observation_id
                        )
                    )

                with time_profiler("Fact indexing"):
                    flat_relation = None

                    # Reconstruct fact from storage payload
                    # Add to fact storage list
                    # Add relation to context entities
                    if fact_transport_payload.has_relation():

                        _flat_fact = FlatFact(fact_transport_payload.fact)
                        _flat_fact[FlatFact.METADATA_TIME_INSERT] = now

                        # Validate fact
                        _flat_fact = await _validate_fact(_flat_fact)

                        # Add fact to storage
                        storage_facts.append(_flat_fact)

                        # If has fact should have relation
                        if fact_transport_payload.relation:
                            # Reconstruct relation from storage payload NOT  NONE)
                            flat_relation: FlatRelation = _get_relation(fact_transport_payload, session_id)

                            # Validate
                            flat_relation = await _validate_relation(_flat_fact, flat_relation)

                            # Add to context entities
                            relation_data_hash = flat_relation[FlatRelation.DATA_HASH]
                            rel_pk = flat_relation[FlatRelation.ENTITY_PK]

                            index_key = (rel_pk, relation_data_hash)
                            indexed_entities_by_id[index_key] = flat_relation

                            # Include relation as an entity in obs_2_ent
                            obs_2_entity.append(get_rel_2_entity_object(
                                observation_id,
                                flat_relation,
                                session_id=session_id
                            ))

                with time_profiler("Entity indexing"):
                    # Reconstruct Context Entities from storage payload
                    flat_context_entities = _get_context_entities(fact_transport_payload)
                    for context_entity in flat_context_entities:

                        if context_entity.get(FlatEntityHistory.ENTITY_ID, None) is None:
                            # DO NOT save abstract entities
                            continue

                        ent_id = context_entity[FlatEntityHistory.ENTITY_PK]
                        ent_data_hash = context_entity.get(FlatEntityHistory.DATA_HASH, None)

                        # Must index by id and data_hash as there can be multiple entities with same id but different data_hash
                        index_key = (ent_id, ent_data_hash)
                        indexed_entities_by_id[index_key] = context_entity

                        # Get context entities in observation
                        obs_2_entity.append(get_obs_2_entity_object(
                            observation_id,
                            context_entity,
                            session_id=session_id
                        ))

            # Save facts
            await _save_facts(transport_context, storage_facts)

            # Save texts
            await _save_texts(transport_context, sys_texts, flat_relation, fact_transport_payload.source_id)

            # Get entities to store
            storage_context_entities = list(indexed_entities_by_id.values())

            if storage_context_entities:

                # Save entity global identifiers
                await _save_entity_gids(transport_context, fact_transport_payload.gids)

                # Get changed entities
                entities_to_save = list(_yield_not_saved_entities(storage_context_entities))

                logger.dev_info(
                    f"Entity: {len(entities_to_save)} out of {len(storage_context_entities)} entities sent to storage due to {global_settings.entity_cache_ttl}s cache.")

                if entities_to_save:

                    # Save Context Entities
                    await _save_entity_history(transport_context, entities_to_save)

                    # Save Entities Last Properties
                    # WARNING: It overrides old properties and keeps the newest. This is by design.
                    # WARNING: IT is used by System 1 memory for quick search.
                    await _save_properties(transport_context, entities_to_save, queue=False)

                    # Save entity in observation.
                    await _store_ent_2_obs(transport_context, obs_2_entity)

                    # Save entity relation to observation - ALERT THIS MAYBE DUPLICATE
                    # BUT IT SAVES entity per each change
                    await _store_obs_2_entity(transport_context, obs_2_entity)

                    # DISABLED: Save in cache for 1h if no traits change
                    if False and global_settings.entity_cache_ttl > 0:
                        # Delete old and set new cached entities
                        ttl = global_settings.entity_cache_ttl  # Default 1h

                        _update_cached_entities(entities_to_save, ttl)

            if storage_timers:
                # Save Timers
                await _save_timers(transport_context, storage_timers)


def save_event_in_queue(context: TransportContext,
                        bulk_storage_payload: List[dict]):
    # Storage payload after deserialization lose its types, all are dict
    logger.debug(f"Accepted for batching payload with {len(bulk_storage_payload)} events.")
    return BulkedResult(bulk_storage_payload)  # we need one by one


async def event_storage_worker(fact_transport_payload_list: List[FactTransportPayload]):
    if fact_transport_payload_list:
        with deferred_execution() as defer:
            status = await defer(save_event_in_queue)(fact_transport_payload_list).push(
                FACT_STORAGE_TAG,
                TransportContext.build(get_context(), params={RECORDS: len(fact_transport_payload_list)}),
                batcher=BatcherConfig(
                    func=save_events_in_queue,
                    min_size=200,
                    max_size=10000,
                    timeout=3
                ),
                adapter=queue_adapter(queue_type.STORAGE)
            )

            if status.logs:
                log_handler.add(status.logs)

            if status.error:
                raise status.error
