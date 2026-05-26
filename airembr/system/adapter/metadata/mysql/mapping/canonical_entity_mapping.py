from airembr.model.metadata.sys_canonical_entity import CanonicalEntity, CanonicalEntityProperty, PropertyType
from airembr.model.system.context import get_context
from airembr.system.adapter.metadata.mysql.schema.table import CanonicalEntityTable, CanonicalEntityPropertyTable


def map_to_canonical_entity_table(entity: CanonicalEntity) -> CanonicalEntityTable:
    context = get_context()
    return CanonicalEntityTable(
        id=entity.id,
        tenant=context.tenant,
        production=context.production,
        name=entity.name,
        ontology_id=entity.ontology_id,
        classification=entity.classification,
        identification=entity.identification,
    )


def map_to_canonical_entity(table: CanonicalEntityTable) -> CanonicalEntity:
    return CanonicalEntity(
        id=table.id,
        production=table.production,
        running=table.running,
        name=table.name,
        ontology_id=table.ontology_id,
        classification=table.classification,
        identification=table.identification,
    )


def map_to_canonical_entity_property_table(prop: CanonicalEntityProperty) -> CanonicalEntityPropertyTable:
    context = get_context()
    return CanonicalEntityPropertyTable(
        id=prop.id,
        tenant=context.tenant,
        production=context.production,
        name=prop.name,
        type=prop.type.value,
        default=prop.default,
        required=prop.required,
        canonical_entity_id=prop.canonical_entity_id,
    )


def map_to_canonical_entity_property(table: CanonicalEntityPropertyTable) -> CanonicalEntityProperty:
    return CanonicalEntityProperty(
        id=table.id,
        production=table.production,
        running=table.running,
        name=table.name,
        type=PropertyType(table.type),
        default=table.default,
        required=table.required,
        canonical_entity_id=table.canonical_entity_id,
    )
