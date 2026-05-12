from typing import Tuple, Optional

from airembr.system.adapter.metadata.mysql.mapping.sys_embedding_setting_mapping import map_to_embedding, map_to_embedding_table
from airembr.system.adapter.metadata.mysql.schema.table import EmbeddingTable
from airembr.model.metadata.sys_embedding_setting import EmbeddingSetting

from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.select_result import SelectResult


class EmbeddingService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(EmbeddingTable, search, limit, offset)

    async def load_by_id(self, embedding_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(EmbeddingTable, primary_id=embedding_id)

    async def delete_by_id(self, embedding_id: str) -> Tuple[bool, Optional[EmbeddingSetting]]:
        return await self.proxy.delete_by_id_in_deployment_mode(
            EmbeddingTable,
            map_to_embedding,
            primary_id=embedding_id
        )

    async def insert(self, embedding: EmbeddingSetting):
        return await self.proxy.replace(EmbeddingTable, map_to_embedding_table(embedding))
