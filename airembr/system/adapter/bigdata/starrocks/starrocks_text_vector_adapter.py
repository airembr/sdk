from typing import List

from airembr.sdk.ai.config import embedding_host, embedding_api_key
from airembr.sdk.service.remote.embedding_api_client import EmbeddingApiClient
from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.general.utils.mapping import sys_text_vector_mapping
from airembr.system.adapter.bigdata.starrocks.utils.sql_text import similar_texts_sql


class StarrocksTextVectorAdapter(AdapterRouter):

    async def stream(self, rows: List):
        if rows:
            mapping = sys_text_vector_mapping()
            return await self.adapter.stream(rows, mapping)
        return None

    async def find_similar_texts(self, query: str, limit: int = 10):
        emb_client = EmbeddingApiClient(embedding_host, embedding_api_key)
        response = emb_client.call({"query": query}).get_mapped_embeddings()
        query_vector = response.dense["query"]
        sql = similar_texts_sql(query_vector, limit)
        return await self.adapter.exec(sql)

