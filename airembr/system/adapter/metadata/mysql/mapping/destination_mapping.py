from airembr.model.system.named_entity import NamedEntity
from airembr.model.system.context import get_context
from airembr.model.metadata.sys_destination import Destination, DestinationConfig, DestinationTrigger, DestinationResource
from airembr.system.adapter.metadata.mysql.mapping.utils import split_list
from airembr.system.adapter.metadata.mysql.schema.table import DestinationTable
from airembr.system.adapter.metadata.mysql.utils.serilizer import to_model, from_model

def map_to_destination_table(destination: Destination) -> DestinationTable:
    context = get_context()
    return DestinationTable(
        id=destination.id,
        name=destination.name,

        tenant=context.tenant,
        production=context.production,

        description=destination.description or "",
        destination=from_model(destination.destination),
        enabled=destination.enabled,
        on_profile_change_only=destination.on_profile_change_only,
        trigger_type=destination.trigger_type,
        event_type_id=destination.event_type.id if destination.event_type else None,
        event_type_name=destination.event_type.name if destination.event_type else None,
        source_id=destination.source.id,
        source_name=destination.source.name,
        resource_id=destination.resource.id,
        resource_type=destination.resource.type,
        tags=','.join(destination.tags) if destination.tags else None,
        trigger_type_id=destination.trigger.type.id,
        trigger_type_name=destination.trigger.type.name,
        trigger_config=destination.trigger.config,
    )


def map_to_destination(destination_table: DestinationTable) -> Destination:
    return Destination(
        id=destination_table.id,
        name=destination_table.name,
        description=destination_table.description or "",
        destination=to_model(destination_table.destination, DestinationConfig),
        enabled=destination_table.enabled if destination_table.enabled is not None else False,
        on_profile_change_only=destination_table.on_profile_change_only if destination_table.on_profile_change_only is not None else True,
        trigger_type=destination_table.trigger_type,
        event_type=NamedEntity(
            id=destination_table.event_type_id,
            name=destination_table.event_type_name
        ) if destination_table.event_type_id and destination_table.event_type_name else None,
        source=NamedEntity(
            id=destination_table.source_id or "",
            name=destination_table.source_name or ""
        ),
        resource=DestinationResource(
            id=destination_table.resource_id or "",
            type=destination_table.resource_type or "resource"
        ),
        trigger=DestinationTrigger(
            type=NamedEntity(
                id=destination_table.trigger_type_id,
                name=destination_table.trigger_type_name
            ),
            config=destination_table.trigger_config
        ),
        tags=split_list(destination_table.tags),
        production=destination_table.production,
        running=destination_table.running
    )
