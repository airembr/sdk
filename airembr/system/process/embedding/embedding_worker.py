from typing import List, Optional

from pararun.model.batcher import BatcherConfig
from pararun.model.transport_context import TransportContext
from pararun.publisher.deferer import deferred_execution
from pararun_adapter import queue_type

from airembr.system.logging.log_handler import get_logger, log_handler
from airembr.model.system.job_tags import RT_EMBEDDER_DESTINATION_TAG
from airembr.model.system.context import get_context
from airembr.model.system.observation import Observation
from airembr.model.system.context import ServerContext, Context
from airembr.system.process.dispatching.model.destination_payload import DestinationPayload
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.system.process.dispatching.trigger_interface import TriggerInterface
from airembr.system.process.preconfig.setup_destination_triggers import DT_EMBEDDER
from airembr.system.process.dispatching.dispatchers import yield_event_destination_work_package

logger = get_logger(__name__)


async def batched_embedding_worker(context: TransportContext, batch: List[dict], metadata: Optional[dict] = None):
    with ServerContext(Context(**context.as_context())):
        observations = []
        destinations = set()
        for destination_instance, observation in batch:
            observations.append(observation)
            destinations.add(destination_instance)

        for destination in destinations:
            await destination.dispatch(observations,
                                       job_name="real-time-embedding")


async def embedding_dispatch_in_queue(context: TransportContext,
                                      destination_work_pack: dict,
                                      observation_as_dict: dict):
    destination_instance = DestinationPayload(
        **destination_work_pack).get_destination_instance(debug=context.production)  # type: TriggerInterface

    return destination_instance, Observation(**observation_as_dict)


def _get_as_int(value):
    if isinstance(value, str) and not value.isdigit():
        value = 100
    else:
        value = int(value)
    return value


async def embedding_worker(observation: Observation, queued: Optional[bool] = True):
    if observation:
        context = get_context()

        async for observation, destination_work_pack in yield_event_destination_work_package(
                observation, DT_EMBEDDER):

            trigger = destination_work_pack.destination.trigger
            observation_as_dict = observation.model_dump(mode='json')

            with deferred_execution() as defer:
                max_size = _get_as_int(trigger.get_config_as_int('bulk_size', 100))
                timeout = _get_as_int(trigger.get_config_as_int('bulk_timeout', 5))
                adapter = queue_adapter(queue_type.DESTINATION)

                job_tag = f"{RT_EMBEDDER_DESTINATION_TAG}-{destination_work_pack.destination.id}"

                if not queued:
                    # This is to test compatibility
                    observation_as_dict = adapter.assure_serialization_compatibility(observation_as_dict)
                    destination_work_pack = adapter.assure_serialization_compatibility(destination_work_pack)

                # Send event outbound
                status = await defer(embedding_dispatch_in_queue)(
                    destination_work_pack,
                    observation_as_dict
                ).push(job_tag,  # Job tag is used for batching
                       TransportContext.build(context),
                       adapter=adapter,
                       batcher=BatcherConfig(
                           func=batched_embedding_worker,
                           min_size=1,
                           max_size=max_size,
                           timeout=timeout
                       ),
                       queued=queued
                       )

                if status.logs:
                    log_handler.add(status.logs)

                if status.error:
                    raise status.error

