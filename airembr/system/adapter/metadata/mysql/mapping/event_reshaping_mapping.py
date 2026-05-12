from airembr.model.system.context import get_context
from airembr.model.metadata.sys_evt_reshaping import EventReshapingSchema, ReshapeSchema
from airembr.model.system.named_entity import NamedEntity
from airembr.system.adapter.metadata.mysql.mapping.utils import split_list
from airembr.system.adapter.metadata.mysql.schema.table import EventReshapingTable
from airembr.system.adapter.metadata.mysql.utils.serilizer import to_model, from_model


def map_to_event_reshaping_table(event_reshaping: EventReshapingSchema) -> EventReshapingTable:
    context = get_context()

    return EventReshapingTable(
        id=event_reshaping.id,
        entity_type=event_reshaping.entity_type,
        name=event_reshaping.name,
        description=event_reshaping.description or "No description provided",
        reshaping=from_model(event_reshaping.reshaping),
        tags=','.join(event_reshaping.tags),  # Convert list of tags to a comma-separated string
        event_type=event_reshaping.event_type,
        event_source_id=event_reshaping.event_source.id,
        event_source_name=event_reshaping.event_source.name,
        enabled=event_reshaping.enabled if event_reshaping.enabled is not None else False,  # Set default value for bool

        tenant = context.tenant,
        production = context.production
    )

def map_to_event_reshaping(event_reshaping_table: EventReshapingTable) -> EventReshapingSchema:
    return EventReshapingSchema(
        id=event_reshaping_table.id,
        entity_type=event_reshaping_table.entity_type,
        name=event_reshaping_table.name,
        description=event_reshaping_table.description,
        reshaping=to_model(event_reshaping_table.reshaping, ReshapeSchema),
        tags=split_list(event_reshaping_table.tags),
        event_type=event_reshaping_table.event_type,
        event_source=NamedEntity(id=event_reshaping_table.event_source_id, name=event_reshaping_table.event_source_name),
        enabled=event_reshaping_table.enabled if event_reshaping_table.enabled is not None else False,  # Set default value for bool

        production=event_reshaping_table.production,
        running=event_reshaping_table.running
    )
