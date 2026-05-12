from typing import List

from pararun.model.batcher import BatcherConfig
from pararun.model.status import DispatchStatus
from pararun.model.transport_context import TransportContext, RECORDS
from pararun.publisher.deferer import deferred_execution
from pararun_adapter import queue_type
from pararun.service.error_handler import fallback_on_error

from airembr.model.system.job_tags import OBSERVATION_COLLECTOR_TAG
from airembr.model.system.headers import Headers
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.system.process.collection.observation_manager import bulk_observations_in_queue, observations_in_queue


async def collector_worker(transport_context: TransportContext, observations: List[dict],
                           headers: Headers) -> DispatchStatus:
    batch_config = BatcherConfig(
        func=bulk_observations_in_queue,
        min_size=1,
        max_size=5000,
        timeout=3
    )

    with deferred_execution() as defer:
        transport_context.properties = {RECORDS: len(observations)}
        status = await defer(observations_in_queue)(headers, observations).push(
            OBSERVATION_COLLECTOR_TAG,
            transport_context,
            batcher=batch_config,
            adapter=queue_adapter(queue_type.COLLECTOR),
            # This adapter required this function args: (headers, observations)
            on_error=fallback_on_error  # Fallback server
        )

        return status
