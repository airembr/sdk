from airembr.model.system.context import get_context

from airembr.model.metadata.sys_evt_validation import EventValidator, ValidationSchema
from airembr.system.adapter.metadata.mysql.mapping.utils import split_list
from airembr.system.adapter.metadata.mysql.schema.table import EventValidationTable
from airembr.system.adapter.metadata.mysql.utils.serilizer import to_model, from_model


def map_to_event_validation_table(event_validator: EventValidator) -> EventValidationTable:

    context = get_context()
    return EventValidationTable(
        id=event_validator.id,
        tenant=context.tenant,
        production=context.production,
        name=event_validator.name,
        description=event_validator.description,
        validation=from_model(event_validator.validation),
        ttl=event_validator.ttl,
        tags=",".join(event_validator.tags),
        event_type=event_validator.event_type,
        entity_type=event_validator.entity_type,
        enabled=event_validator.enabled
    )

def map_to_event_validation(table: EventValidationTable) -> EventValidator:
    return EventValidator(
        id=table.id,
        name=table.name,
        description=table.description,
        entity_type=table.entity_type,
        event_type=table.event_type,
        tags=split_list(table.tags),  # Convert string back to list
        validation=to_model(table.validation, ValidationSchema) if table.validation else None,
        ttl=table.ttl,
        enabled=table.enabled,

        production=table.production,
        running=table.running
    )
