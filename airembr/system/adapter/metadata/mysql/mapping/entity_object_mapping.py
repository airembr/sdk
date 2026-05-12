from airembr.system.adapter.metadata.mysql.schema.table import EntityObjectTable
from airembr.model.entity_object import EntityObject
from airembr.model.system.context import get_context


def map_to_entity_object_table(entity_object: EntityObject) -> EntityObjectTable:
    context = get_context()
    data = entity_object.model_dump(exclude={"running": ..., "production": ...})
    data['tenant'] = context.tenant
    data['production'] = context.production
    data['id'] = f"{data['type']}-{data['tenant']}"
    return EntityObjectTable(**data)


def map_to_entity_object(entity_object_table: EntityObjectTable) -> EntityObject:
    return EntityObject(
        id=entity_object_table.id,
        description=entity_object_table.description,
        label=entity_object_table.label,
        type=entity_object_table.type,
        pk_id=entity_object_table.pk_id,
        mg_id=entity_object_table.mg_id,
        table=entity_object_table.table,
        lock=entity_object_table.lock,
        enabled=entity_object_table.enabled,
        properties=entity_object_table.properties,
        stitches=entity_object_table.stitches,
        requires_consent=entity_object_table.requires_consent,
        requires_merging=entity_object_table.requires_merging,
        consents=entity_object_table.consents,
        hash=entity_object_table.hash,
        production=entity_object_table.production,
        running=entity_object_table.running
    )
