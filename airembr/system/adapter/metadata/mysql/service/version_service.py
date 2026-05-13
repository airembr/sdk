from typing import Optional

from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.model.system.version import Version
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.adapter.metadata.mysql.mapping.version_mapping import map_to_version_table, map_to_version
from airembr.system.adapter.metadata.mysql.schema.table import VersionTable
from airembr.system.adapter.metadata.mysql.service.user_service import _where_with_context
from airembr.sdk.storage.metadata.query.select_result import SelectResult

logger = get_logger(__name__)

# --------------------------------------------------------
# This Service Runs in Production and None-Production Mode
# It is PRODUCTION CONTEXT-LESS
# --------------------------------------------------------

class VersionService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, limit: int = None, offset: int = None) -> SelectResult:
        where = _where_with_context()

        return await self.proxy.select_query(VersionTable,
                                        where=where,
                                        limit=limit,
                                        offset=offset)

    async def upsert(self, version: Version):
        return await self.proxy.replace(VersionTable, map_to_version_table(version))

    async def load_by_version(self, version: str) -> Optional[Version]:
        where = _where_with_context(  # tenant only mode
            VersionTable.api_version == version
        )

        records = await self.proxy.select_query(VersionTable, where=where)

        if not records.exists():
            return None

        return records.map_first_to_object(map_to_version)
