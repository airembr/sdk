from pararun_adapter import queue_type
from pararun.model.transport_context import TransportContext

from airembr.system.process.dispatching.trigger_worker import trigger_worker, trigger_dispatch_in_queue
from airembr.model.system.observation import Observation
from airembr.model.system.context import get_context
from airembr.model.system.headers import Headers
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.system.logging.log_handler import get_logger

logger = get_logger(__name__)

async def run_triggers(headers: Headers,
                       observation: Observation):

    if headers.should_process(service='destination'):

        observation_as_dict = observation.model_dump(mode='json')

        # Background worker
        if headers.should_queue(service='destination'):
            logger.info(f"Triggering destination process for {observation.source.id}")
            await trigger_worker(observation_as_dict)
        else:
            adapter = queue_adapter(queue_type.DESTINATION)
            observation_as_dict = adapter.assure_serialization_compatibility(observation_as_dict)
            transport_context = TransportContext.build(get_context())
            await trigger_dispatch_in_queue(transport_context, observation_as_dict, debug=False)
            logger.info(f"Triggering realtime destination for {observation.source.id}")




