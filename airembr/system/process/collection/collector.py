from time import time
from typing import List, Optional, Dict, Tuple

from pararun.model.status import DispatchStatus
from pararun_adapter import queue_type
from pararun.model.transport_context import TransportContext

from airembr.system.process.ai.memory.conversation.memorizer import memorizer

from airembr.core.data.chunker import chunk_generator
from airembr.model.system.headers import Headers
from airembr.model.system.observation import Observation
from airembr.model.system.context import get_context
from airembr.system.config.global_config import global_settings
from airembr.system.process.monitoring.metrics.metrics import QUEUE_PHASE_LATENCY
from airembr.system.config.sys_config import sys_config
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.logging import extra_info
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.system.process.collection.observation_manager import compute_and_save_events
from airembr.system.process.collection.collector_worker import collector_worker

logger = get_logger(__name__)
_measures = []


async def _observe(observations: List[Observation] | Observation, headers: Headers) -> Tuple[
    Optional[dict], DispatchStatus | None]:
    start = time()

    if isinstance(observations, Observation):
        observations: List[Observation] = [observations]

    collector = Collector(headers, observations)

    # If observation is a chat then memorize conversation
    async with memorizer(collector) as conversation_memory:  # Conversation_memory can be None
        no_of_records, dispatch_status = await collector.register_observation()

    # No DispatchStatus if not sent to the queue
    if dispatch_status and dispatch_status.error:
        logger.error(
            f"Collection failed. No records consumed. Details: {str(dispatch_status.error)}",
            extra=extra_info.build(origin='Collector API', error_number='API-0002')
        )
    else:
        passed_time = time() - start
        if global_settings.enable_prometheus:
            QUEUE_PHASE_LATENCY.labels(
                phase='collector'
            ).observe(passed_time)
            logger.debug(f"Collection finished in {passed_time}s. Number of records consumed: {no_of_records}")

    return conversation_memory, dispatch_status


class Collector:

    def __init__(self, headers: Headers, observations: List[Observation]):
        self._observations = observations
        self._headers = headers
        self._ttls = None
        self._chat_ids = None
        self._context_windows = None

        context = get_context()

        self.transport_context = TransportContext.build(context)

        if sys_config.api_key and headers.get('x-api-key', None) != sys_config.api_key:
            raise PermissionError("Invalid API KEY.")

    def _filter_not_allowed_observations(self):

        for observation in self._observations:
            if observation.source.id.startswith("@"):
                logger.warning(f"Internal event sources ({observation.source.id}) are not allowed via API.")
                continue

            if sys_config.disallow_bot_traffic and self._headers.is_bot():
                logger.warning(f"Traffic from bot is not allowed.")
                continue

            yield observation

    def _clean(self):
        for observation in self._observations:
            if observation.source:
                observation.source.id = str(observation.source.id).strip()

            # Clean traits if no consents
            for link, entity in observation.entities.root.items():
                if entity.is_consent_granted():
                    continue

                entity.traits = {}

                logger.info(f"Entity {entity.instance} did not meet the required consents. "
                            f"Traits deleted.")

    async def register_observation(self) -> Tuple[int, DispatchStatus | None]:

        self._observations = [observation for observation in self._observations if observation.is_consent_granted()]

        self._clean()
        self._observations = list(self._filter_not_allowed_observations())

        no_of_observations = len(self._observations)
        if no_of_observations == 0:
            return 0, None

        result = no_of_observations
        if self._headers.should_queue(service='collect'):
            logger.dev_info(f"Queued payload.")

            # Chunk so there are not more than 20 observations per queue message
            # Protection against huge messages.
            status = None
            for observation_chunk in chunk_generator(self._observations, 20, True):
                observation_dicts = [observation.model_dump(mode='json') for observation in observation_chunk]

                status = await collector_worker(
                    self.transport_context,
                    observation_dicts,  # Must be dicts
                    self._headers  # Must be dicts
                )
                # Finish earlier if error
                # TODO will loose data if error in chunk, or data will be resent
                if status.error:
                    return result, status

            return result, status

        else:
            logger.dev_info(f"Realtime payload.")

            observation_dicts = [observation.model_dump(mode='json') for observation in self._observations]

            # Converts DotDicts to dicts etc. for transportation
            adapter = queue_adapter(queue_type.COLLECTOR)
            observation_dicts: List[dict] = adapter.assure_serialization_compatibility(observation_dicts)

            # Runs in the same context as self.transport_context
            result = await compute_and_save_events(
                get_context(),
                observation_dicts,
                self._headers,
            )

            return result, None

    def _yield_chat_ids(self):
        for observation in self._observations:
            if observation.is_chat():
                session_id = observation.get_session_id()
                if session_id is not None:
                    yield session_id

    def get_chat_ids(self):
        if self._chat_ids is None:
            self._chat_ids = list(self._yield_chat_ids())
        return self._chat_ids

    def get_semantic_text(self):
        for observation in self._observations:
            texts = []
            if observation.relation:
                for rel in observation.relation:
                    if rel.has_sematic_part():
                        if rel.text.description:
                            texts.append(f"[{rel.ts}] {rel.actor.link}: {rel.text.description}")

                yield observation.get_session_id(), observation.is_chat(), observation.get_chat_ttl(), observation.should_chat_ttl_be_overridden(), texts

    def _yield_compression_sizes(self):
        for observation in self._observations:
            session_id = observation.get_session_id()
            if session_id is not None:
                yield session_id, observation.get_chat_compression_trigger()

    def get_compression_sizes(self) -> Dict[str, int]:
        if self._context_windows is None:
            self._context_windows = {k: v for k, v in self._yield_compression_sizes()}
        return self._context_windows

    def _yield_ttls(self):
        for observation in self._observations:
            session_id = observation.get_session_id()
            if session_id is not None:
                yield session_id, observation.get_chat_ttl()

    def get_ttls(self) -> Dict[str, int]:
        if self._ttls is None:
            self._ttls = {k: v for k, v in self._yield_ttls()}
        return self._ttls

    def get_ttl(self, session_id, default=0):
        return self.get_ttls().get(session_id, default)

    def get_participants(self):
        participants = {}
        for observation in self._observations:
            if observation.entities:
                participants[observation.session.id] = observation.get_entities()
        return participants
