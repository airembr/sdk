from typing import List, Optional, Tuple

from durable_dot_dict.dotdict import DotDict

from airembr.system.logging import extra_info
from airembr.sdk.service.dot_accessor import DotAccessor
from airembr.model.metadata.sys_evt_reshaping import EventReshapingSchema
from airembr.system.adapter.metadata.mysql.interface import event_reshaping_dao
from airembr.system.logging.log_handler import get_logger
from airembr.system.process.collection.reshaping.payload_reshaper import PayloadReshaper

logger = get_logger(__name__)


def _reshape_event_properties(
        entity_type: str,
        flat_event_entity: DotDict,
        reshape_schemas: Optional[List[EventReshapingSchema]]):
    resharper = PayloadReshaper(
        # Only this data can be used in the reshaping
        dot=DotAccessor(
            event=flat_event_entity
        )
    )
    return resharper.reshape(entity_type=entity_type, schemas=reshape_schemas)


async def _reshape_event_payload_properties(entity_type: str, event_type: str, flat_event_entity: DotDict) -> Optional[
    Tuple[dict, dict, Optional[dict]]]:
    # Load definition
    reshape_schemas: Optional[List[EventReshapingSchema]] = await event_reshaping_dao.load_and_convert_reshaping(
        event_type)

    if reshape_schemas is not None:
        return _reshape_event_properties(entity_type, flat_event_entity, reshape_schemas)
    return None


async def reshape_event(entity_type: str, event_id: str, event_type: str, data: DotDict) -> DotDict:
    try:
        reshaped = await _reshape_event_payload_properties(entity_type, event_type, data)

        # Blocks event_context, session_context
        if not reshaped:
            return data

        event_properties, event_context, session_context = reshaped

        if not event_properties:
            return data

        return DotDict(event_properties)

    except Exception as e:
        logger.warning(
            f"Reshaping error. Details {str(e)}",
            extra=extra_info.exact(
                origin='event-reshaping',
                package=__name__,
                class_name='reshape_event',
                event_id=event_id,
                entity_id=None,
                error_number="E-0013"
            )
        )
        return data
