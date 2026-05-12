from typing import List

from durable_dot_dict.dotdict import DotDict

from airembr.model.system.observation import Observation
from airembr.model.metadata.sys_destination import Destination
from airembr.system.process.dispatching.utils import get_destination_resource
from airembr.system.adapter.metadata.mysql.interface import destination_dao
from airembr.system.logging import extra_info
from airembr.core.exception.exception_service import get_traceback
from airembr.system.logging.log_handler import get_logger

logger = get_logger(__name__)


def filter_by(destinations, event_type: str, source_id: str):
    for destination in destinations:
        config = DotDict(destination.trigger.config)
        allowed_event_type = config.get_or_none('event_type.id')
        allowed_source_id = config.get_or_none('source.id')

        if allowed_event_type is None and allowed_source_id is None:
            yield destination
        elif allowed_event_type is None and config.get_or_none('source.id') == source_id:
            yield destination
        elif allowed_source_id is None and config.get_or_none('event_type.id') == event_type:
            yield destination
        elif config.get_or_none('event_type.id') == event_type and config.get_or_none('source.id') == source_id:
            yield destination


async def yield_event_destination_work_package(observation: Observation, trigger_type: str):
    # Reads from cache
    loaded_destinations: List[Destination] = await destination_dao.load_enabled_destinations(trigger_type)
    observation_as_dict = observation.model_dump()

    no_of_loaded_destinations = len(loaded_destinations)
    if no_of_loaded_destinations == 0:
        logger.debug(f"Loaded {no_of_loaded_destinations} destinations for trigger type `{trigger_type}`")
    else:
        logger.info(f"Loaded {no_of_loaded_destinations} destinations for trigger type `{trigger_type}`")

    try:
        source_id = observation.source.id

        for relation in observation.relation:

            event_type = relation.label

            # Filter based on configured event type.
            _destinations = list(filter_by(loaded_destinations, event_type, source_id))

            # Skip if not destination
            if not _destinations:
                continue

            async for destination_work_package in get_destination_resource(_destinations):
                observation_as_dict['relation'] = [relation.model_dump()]
                yield Observation(**observation_as_dict), destination_work_package


    except Exception as e:
        logger.error(
            str(e),
            extra=extra_info.exact(
                error_number="E-0011",
                flow_id=None,
                node_id=None,
                event_id=None,
                entity_id=None,
                origin='destination',
                package=__name__,
                traceback=get_traceback(e)
            )
        )
