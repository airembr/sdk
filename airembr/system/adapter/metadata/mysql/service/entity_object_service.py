from typing import Optional, Tuple

from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.table_filtering import where_tenant_and_mode_context

from airembr.model.entity_object import EntityObject
from airembr.system.adapter.metadata.mysql.mapping.entity_object_mapping import map_to_entity_object_table, \
    map_to_entity_object
from airembr.system.adapter.metadata.mysql.schema.table import EntityObjectTable
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from sqlalchemy import and_


def to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in obj.__table__.columns}


class EntityObjectService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(EntityObjectTable, search, limit, offset)

    async def load_all_with_table(self) -> SelectResult:
        return await self.proxy.load_by_query_in_deployment_mode(EntityObjectTable,
                                                                 where=EntityObjectTable.table.isnot(None))

    async def load_by_id(self, entity_object_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(EntityObjectTable, primary_id=entity_object_id)

    async def load_by_type(self, entity_type: str, only_enabled: bool = False) -> SelectResult:
        if only_enabled:
            where = and_(EntityObjectTable.type == entity_type, EntityObjectTable.enabled == True)
        else:
            where = EntityObjectTable.type == entity_type
        return await self.proxy.load_by_query_in_deployment_mode(EntityObjectTable,
                                                                 where=where)

    async def delete_by_id(self, entity_object_id: str) -> Tuple[bool, Optional[EntityObject]]:
        return await self.proxy.delete_by_id_in_deployment_mode(EntityObjectTable, map_to_entity_object,
                                                                primary_id=entity_object_id)

    async def delete_by_entity_type(self, entity_object_id: str) -> Tuple[bool, Optional[EntityObject]]:
        return await self.proxy.delete_by_id_in_deployment_mode(EntityObjectTable, map_to_entity_object,
                                                                primary_id=entity_object_id)

    async def insert(self, entity_object: EntityObject):
        entity_object_table = map_to_entity_object_table(entity_object)

        local_session = self.proxy.ts.client.get_session()
        async with local_session() as session:
            async with session.begin():
                upsert_object_stmt = self.proxy.insert_stmt(EntityObjectTable, entity_object_table)
                await session.execute(upsert_object_stmt)

                # Assuming the primary key field is named 'id'
                return getattr(entity_object_table, 'id', None)

    async def load_enabled(self, limit: Optional[int] = None) -> SelectResult:
        where = where_tenant_and_mode_context(
            EntityObjectTable,
            EntityObjectTable.enabled == True
        )
        return await self.proxy.select_in_deployment_mode(
            EntityObjectTable,
            where=where,
            limit=limit,
            offset=0
        )
