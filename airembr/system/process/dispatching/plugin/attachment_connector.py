import hashlib
from typing import List

from airembr.system.process.dispatching.trigger_interface import TriggerInterface

from pararun.model.transport_context import TransportContext
from pararun.publisher.deferer import deferred_execution
from pararun_adapter import queue_type

from airembr.core.data.chunker import chunk_generator
from airembr.system.process.logging.log_handler import get_logger
from airembr.model.api.request.observation import Observation
from airembr.model.system.job_tags import DF_EVENT_ATTACHMENT_DESTINATION_TAG
from airembr.system.utils.text.formaters import format_observation
from airembr_sdk.core.date import now_in_utc
from airembr.model.system.context import get_context
from airembr.system.adapter.queue.queue_adapter import queue_adapter

logger = get_logger(__name__)

def _convert_to_table_row(job_name, rel_id, status):
    job_id = hashlib.md5(job_name.encode()).hexdigest()
    return {
        "rel_id": rel_id,
        "job_id": job_id,
        "ts": now_in_utc(),
        "job_name": job_name,
        "job_status": status
    }


async def attachment_worker(context: TransportContext, observations: List[Observation], job_name: str):
    print('context', context)
    print('jon-name', job_name)
    for observation in observations:
        print(format_observation(observation))


class FactAttachmentConnector(TriggerInterface):

    async def dispatch(self, observations: List[Observation], job_name: str = None):
        rows = []
        try:
            for observations_batch in chunk_generator(observations, batch_size=1000, proceed_if=True):

                # Queue
                observations_batch = list(observations_batch)

                adapter = queue_adapter(queue_type.ATTACHMENTS)
                with deferred_execution() as defer:
                    status = await defer(attachment_worker)(observations_batch, job_name).push(
                        DF_EVENT_ATTACHMENT_DESTINATION_TAG,
                        TransportContext.build(get_context()),
                        adapter=adapter
                    )

                    if status.error:
                        raise status.error

                    return status

                # for observation in observations_batch:
                #     rows.append(_convert_to_table_row(job_name, observation.id, "pending"))
        finally:
            if rows:
                # Save metadata
                logger.info(f"Marked {len(rows)} facts as processed.")


