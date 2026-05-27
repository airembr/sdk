from durable_dot_dict.dotdict import DotDict
from typing import List, Tuple, Optional, AsyncGenerator

from pydantic import ValidationError

from pararun.model.transport_context import TransportContext
from pararun_adapter import queue_type

from airembr.model.system.transport_payload import FactTransportPayload, ObsTransportPayload
from airembr.model.system.headers import Headers
from airembr.model.api.request.observation import Observation
from airembr.model.system.context import ServerContext, Context
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.system.process.dispatching.trigger_manager import run_triggers
from airembr.system.process.embedding.embedding_manager import run_embedding
from airembr.system.process.collection.computation.event_computer import compute_events
from airembr.system.process.sourcing.source_validation import valid_sources
from airembr.system.process.collection.fact_worker import save_events_in_queue, event_storage_worker
from airembr.system.process.collection.observation_worker import obs_storage_worker, save_obs_in_queue

logger = get_logger(__name__)


def _get_valid_observation(observations) -> List[Observation]:
    _observations = []
    for observation in observations:
        try:
            _observations.append(Observation(**observation))
        except ValidationError as e:
            logger.warning(f"Skipped due to validation error: {e}")
    return _observations


async def valid_observations(headers: Headers,
                             observations: List[dict]):
    observations: List[Observation] = _get_valid_observation(observations)

    headers = Headers(headers)
    sources = {observation.source.id for observation in observations}

    # Fetch allowed bridges from header x-bridge
    allowed_bridge = headers.get('x-bridge', 'rest')
    allowed_bridge = allowed_bridge.split(',')

    valid_source_ids = [id async for id in valid_sources(headers, sources, allowed_bridges=allowed_bridge)]
    for observation in observations:
        if observation.source.id not in valid_source_ids:
            logger.warning(
                f"Event source `{observation.source.id}` is not allowed. Check bridge type. Allowed types [{allowed_bridge}].")
            continue

        # Valid observation will have source_id in traits
        if observation.traits is None:
            observation.traits = {}

        observation_traits = DotDict(observation.traits)
        observation_traits['source.id'] = observation.source.id
        # TODO add source name
        # Valid observation will have session_id in traits
        if observation.has_session():
            observation_traits['session.id'] = observation.session.id
        observation.traits = observation_traits.to_dict()

        yield observation


async def bulk_observations_in_queue(
        context: TransportContext,
        batch: List[Tuple[List[dict], Headers]],
        metadata: Optional[List[dict]] = None
):
    with ServerContext(Context(**context.as_context())) as cm:
        for observations, headers in batch:
            await compute_and_save_events(cm.context, observations, Headers(headers))


async def observations_in_queue(context: TransportContext,
                                headers: Headers,
                                observations: List[dict]):
    return observations, headers


async def _store_observations(context,
                              headers: Headers,
                              obs_transport_list: List[ObsTransportPayload]):
    if headers.should_process(service='store-observation'):
        if headers.should_queue(service='store-observation'):
            # Background worker
            # Save observations - deferred
            await obs_storage_worker(obs_transport_list)
        else:
            # Get one list of observations
            transport_context = TransportContext.build(context)

            # Converts DotDicts to dicts etc. for transportation
            adapter = queue_adapter(queue_type.STORAGE)

            # Assert and convert to transport type WHICH is DICT
            obs_transport_list: List[dict] = adapter.assure_serialization_compatibility(obs_transport_list)

            await save_obs_in_queue(transport_context, batch=obs_transport_list, queue=False)


async def _store_facts(context,
                       headers: Headers,
                       fact_transport_list: List[FactTransportPayload]):
    # Background worker?
    if headers.should_process(service='store'):
        # Should be queued
        if headers.should_queue(service='store'):

            # Save events - deferred
            await event_storage_worker(fact_transport_list)

        else:
            # Get one list of events
            transport_context = TransportContext.build(context)

            # Converts DotDicts to dicts etc. for transportation
            adapter = queue_adapter(queue_type.STORAGE)

            # Assert and convert to transport type WHICH is DICT
            fact_transport_list: List[dict] = adapter.assure_serialization_compatibility(fact_transport_list)

            await save_events_in_queue(transport_context, batch=fact_transport_list, queue=False)


async def _yield_valid_observation(headers, observations: List[dict]) -> AsyncGenerator[
    Tuple[
        Observation,
        List[FactTransportPayload]
    ]
    , None]:
    async for observation in valid_observations(headers, observations):
        # Observation, flat_fact, flat_relation, storage_context_entities, timer
        yield observation, [item async for item in compute_events(observation, headers)]


async def compute_and_save_events(context,
                                  observations: List[dict],
                                  headers: Headers):
    sent_records = 0
    single_storage_payload_list: List[FactTransportPayload] = []
    single_observation_list: List[ObsTransportPayload] = []

    # Observations are sent (via request) in bulks. Process each observation individually
    async for observation, storage_payload_list in _yield_valid_observation(headers, observations):
        # storage_payload has [{observation, flat_fact, flat_relation, storage_context_entities, timer}]
        sent_records += 1

        # Bulk all storage payloads from a list of observations
        single_storage_payload_list.extend(storage_payload_list)

        # Add observation transport payload
        single_observation_list.append(ObsTransportPayload(
            id=observation.id,  # we have ID always here
            source_id=observation.source.id,
            session_id=observation.get_session_id(),
            label=observation.label,
            description=observation.text.to_string(),
            ner=observation.text.ner,
            entities=observation.entities.total(),
            metadata_time_create=observation.create_ts,
            metadata_time_insert=observation.insert_ts,
        ))

        # Triggers
        await run_triggers(headers, observation)

        # Embeddings
        await run_embedding(headers, observation)

    # Store observations
    await _store_observations(context, headers, single_observation_list)

    # Store facts
    await _store_facts(context, headers, single_storage_payload_list)

    return sent_records
