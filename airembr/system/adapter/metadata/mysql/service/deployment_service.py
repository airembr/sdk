from typing import Dict

from sqlalchemy.orm import DeclarativeBase

from airembr.sdk.storage.metadata.query.context_filter import context_filter
from airembr.system.decorator.proxy.proxy_decorator import invalidate_cache_proxy
from airembr.sdk.storage.metadata.query.table_filtering import where_with_context
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.model.system.context import get_context
from airembr.system.adapter.metadata.mysql.schema.table import EventSourceTable, \
    ResourceTable, EventValidationTable, EventReshapingTable, \
    EventMappingTable, \
    DestinationTable, SettingTable, \
    EntityObjectTable, Base, SysEntSegmentTable, EmbeddingTable
from sqlalchemy import update, delete

_MAPPING: Dict[str, DeclarativeBase] = {
    'event_source': EventSourceTable,
    'destination': DestinationTable,

    'event_validation': EventValidationTable,
    'event_reshaping': EventReshapingTable,
    'event_mapping': EventMappingTable,

    'resource': ResourceTable,
    'metrics': SettingTable,
    'segment': SysEntSegmentTable,

    'entity_object': EntityObjectTable,
    'embedding_setting': EmbeddingTable,
}


class DeploymentService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    @staticmethod
    async def _unpublish_sql(session, table, condition, tenant):
        # Delete - If deploying to production remove old settings first
        where = context_filter(
            table,
            tenant,
            True,
            condition
        )

        await session.execute(
            delete(table).where(where())
        )

    @staticmethod
    async def _publish_sql(session, table, condition, tenant):
        # Delete - If deploying to production remove old settings first
        where = context_filter(
            table,
            tenant,
            True,
            condition
        )

        await session.execute(
            delete(table).where(where())
        )

        # Now update test setting to be mode production

        where = where_with_context(table, True, condition)

        stmt = (
            update(table)
            .where(where)
            .values(**{
                "production": True
            })
        )

        await session.execute(stmt)

    async def _deployment(self, context, table: Base, condition, deploy):

        if not table:
            raise ValueError("Unknown entity.")

        invalidate_cache_proxy(names=[table.__tablename__])

        local_session = self.proxy.ts.client.get_session()
        if deploy:
            async with local_session() as session:
                async with session.begin():
                    await self._publish_sql(session, table, condition, context.tenant)
                    await session.commit()

            return True

        else:
            # Removes from production
            async with local_session() as session:
                async with session.begin():
                    await self._unpublish_sql(session, table, condition, context.tenant)
                    await session.commit()
                    record = await self.proxy.load_by_query_id(table, condition)
                    return record.exists()

    async def deploy(self, table_name: str, id: str, deploy: bool = True) -> bool:
        mapping = _MAPPING.copy()

        # Workflow
        if True:
            from dagor.interface.deployment import WORKFLOW_TABLE_MAPPING
            mapping.update(WORKFLOW_TABLE_MAPPING)

        table: Base = mapping.get(table_name, None)

        context = get_context()
        local_session = self.proxy.ts.client.get_session()
        async with local_session() as session:
            async with session.begin():
                condition = table.id == id
                result = await self._deployment(context, table, condition, deploy)
                await session.commit()
                return result
