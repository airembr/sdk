from pararun.model.transport_context import TransportContext
from pararun.publisher.deferer import deferred_execution
from pararun_adapter import queue_type

from airembr.model.system.job_tags import RT_EVENT_DESTINATION_TAG
from airembr.model.system.observation import Observation

from airembr.system.process.dispatching.trigger_interface import TriggerInterface
from airembr.system.preconfig.setup_destination_triggers import DT_EVENT_TRIGGER

from airembr.system.process.logging.log_handler import get_logger, log_handler
from airembr.system.config.sys_config import sys_config
from airembr.model.system.context import get_context
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.model.system.context import ServerContext, Context
from airembr.system.process.dispatching.dispatchers import yield_event_destination_work_package

logger = get_logger(__name__)


async def trigger_dispatch_in_queue(context: TransportContext,
                                    observation: dict,
                                    debug):
    # Run in Context
    with (ServerContext(Context(**context.as_context()))):
        # Reconstruct observation
        observation = Observation(**observation)

        async for observation, destination_work_pack in yield_event_destination_work_package(
                observation, DT_EVENT_TRIGGER):

            try:
                # Get destination reference
                destination_instance = destination_work_pack.get_destination_instance(debug)  # type: TriggerInterface

                await destination_instance.dispatch([observation],
                                                    job_name="real-time-event-destination")
            except Exception as e:
                # Catch dispatch errors
                logger.warning(str(e))

async def trigger_worker(observation_as_dict: dict):
    if sys_config.enable_triggers and observation_as_dict:
        debug = not get_context().production

        with deferred_execution() as defer:
            # Send event outbound
            status = await defer(trigger_dispatch_in_queue)(observation_as_dict, debug=debug).push(
                RT_EVENT_DESTINATION_TAG,
                TransportContext.build(get_context()),
                adapter=queue_adapter(
                    queue_type.DESTINATION)
                )

            if status.logs:
                log_handler.add(status.logs)

            if status.error:
                raise status.error
