from airembr.model.metadata.sys_canonical_entity import CanonicalEntity, CanonicalEntityProperty
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from airembr.sdk.storage.metadata.query.table_filtering import (
    where_tenant_and_mode_context,
)
from airembr.system.adapter.metadata.mysql.mapping.canonical_entity_mapping import (
    map_to_canonical_entity,
    map_to_canonical_entity_table,
    map_to_canonical_entity_property_table,
)
from airembr.system.adapter.metadata.mysql.schema.table import (
    CanonicalEntityTable,
    CanonicalEntityPropertyTable,
)


class CanonicalEntityService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(CanonicalEntityTable, search, limit, offset)

    async def load_by_id(self, entity_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(CanonicalEntityTable, primary_id=entity_id)

    async def load_by_name(self, entity_name: str) -> SelectResult:
        return await self.proxy.field_filter(CanonicalEntityTable, CanonicalEntityTable.name, entity_name)

    async def load_by_ontology_id(self, ontology_id: str) -> SelectResult:
        return await self.proxy.field_filter(CanonicalEntityTable, CanonicalEntityTable.ontology_id, ontology_id)

    async def insert(self, entity: CanonicalEntity):
        return await self.proxy.replace(CanonicalEntityTable, map_to_canonical_entity_table(entity))

    async def replace(self, entity: CanonicalEntity):
        return await self.proxy.replace(CanonicalEntityTable, map_to_canonical_entity_table(entity))

    async def delete_by_id(self, entity_id: str):
        return await self.proxy.delete_by_id_in_deployment_mode(
            CanonicalEntityTable, map_to_canonical_entity, primary_id=entity_id
        )

    async def delete_by_ontology_id(self, ontology_id: str):
        where = where_tenant_and_mode_context(
            CanonicalEntityTable,
            CanonicalEntityTable.ontology_id == ontology_id,
        )
        return await self.proxy.delete_query(CanonicalEntityTable, where)


class CanonicalEntityPropertyService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_by_id(self, prop_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(CanonicalEntityPropertyTable, primary_id=prop_id)

    async def load_by_entity_id(self, entity_id: str) -> SelectResult:
        return await self.proxy.field_filter(
            CanonicalEntityPropertyTable,
            CanonicalEntityPropertyTable.canonical_entity_id,
            entity_id,
        )

    async def insert(self, prop: CanonicalEntityProperty):
        return await self.proxy.replace(
            CanonicalEntityPropertyTable,
            map_to_canonical_entity_property_table(prop),
        )

    async def replace(self, prop: CanonicalEntityProperty):
        return await self.proxy.replace(
            CanonicalEntityPropertyTable,
            map_to_canonical_entity_property_table(prop),
        )

    async def delete_by_id(self, prop_id: str):
        return await self.proxy.delete_by_id_in_deployment_mode(CanonicalEntityPropertyTable, primary_id=prop_id)

    async def delete_by_entity_id(self, entity_id: str):
        where = where_tenant_and_mode_context(
            CanonicalEntityPropertyTable,
            CanonicalEntityPropertyTable.canonical_entity_id == entity_id,
        )
        return await self.proxy.delete_query(CanonicalEntityPropertyTable, where)
