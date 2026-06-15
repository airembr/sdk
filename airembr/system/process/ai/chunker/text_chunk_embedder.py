from time import time

from typing import Optional, Dict, List, Tuple

from airembr.model.bigdata.flat_text_vector import FlatTextVector
from airembr.model.system.context import get_context
from airembr.sdk.ai.chunking.text_chunker import get_text_chunker

from airembr.system.adapter.bigdata.general.utils.mapping import sys_text_mapping, sys_text_vector_mapping
from airembr.system.adapter.bigdata.tool.column_mapper import map_to_table_columns
from airembr.system.adapter.metadata.mysql.service.task_service import background_log
from airembr.system.process.logging.log_handler import get_logger
from airembr.sdk.service.remote.llm.llm_adapter import LLMAdapter
from airembr.sdk.ai.config import LLM_PROVIDER, LLM_PROVIDER_API_KEY, LLM_ENTITY_EXTRACTION_MODEL, \
    SECOND_LLM_ENTITY_EXTRACTION_MODEL
from airembr.core.hash.hash import md5
from airembr.model.bigdata.flat_text import FlatText
from airembr.sdk.ai.config import embedding_host, embedding_api_key
from airembr.sdk.service.remote.embedding_api_client import EmbeddingApiClient
from airembr.system.adapter.bigdata.big_data_adapter import bd_text_adapter, bd_text_vector_adapter
from airembr_sdk.client.airembr_chat import AiRembrChatClient
from airembr_sdk.core.date import now_in_utc

logger = get_logger(__name__)
_sys_text_mapping = sys_text_mapping()
_sys_text_vector_mapping = sys_text_vector_mapping()

BULK_SIZE = 500

adapter = LLMAdapter(
    provider=LLM_PROVIDER,
    api_key=LLM_PROVIDER_API_KEY,
    model=LLM_ENTITY_EXTRACTION_MODEL
)

second_adapter = LLMAdapter(
    provider=LLM_PROVIDER,
    api_key=LLM_PROVIDER_API_KEY,
    model=SECOND_LLM_ENTITY_EXTRACTION_MODEL
)

client = AiRembrChatClient(api="http://localhost:4002")


def _collect_all_chunks(data, chunker, model: str, now) -> Tuple[Dict[str, dict], List[str]]:
    chunk_map: Dict[str, dict] = {}
    original_ids: List[str] = []
    for row in data:
        original_id = row['id']
        observation_id = row['observation_id']
        chunks = chunker(row['text_string'])
        chunk_ids = [md5(chunk) for chunk in chunks]
        has_siblings = len(chunks) > 1
        for chunk_id, chunk in zip(chunk_ids, chunks):
            chunk_map[chunk_id] = {
                'text': chunk,
                'parent_id': original_id,
                'observation_id': observation_id,
                'has_siblings': has_siblings,
                'model': model,
                'ts': now,
            }
        original_ids.append(original_id)
    return chunk_map, original_ids


async def _embed_in_batches(chunk_map: Dict[str, dict], emb_client: EmbeddingApiClient,
                      batch_size: int = BULK_SIZE) -> Optional[Dict[str, List[float]]]:
    context = get_context()
    async with background_log("Embedding Chunks Worker", f"Embedding in {context}") as (bts, task_id):
        items = list(chunk_map.items())
        embeddings: Dict[str, List[float]] = {}
        no_of_items = len(items)
        for i in range(0, no_of_items, batch_size):
            batch = {chunk_id: entry['text'] for chunk_id, entry in items[i:i + batch_size]}
            try:
                result = emb_client.call(batch).get_mapped_embeddings()
            except Exception as e:
                if not embedding_host:
                    logger.error(f"Missing embedding API. Error in {context} {e}")
                else:
                    logger.error(f"Unavailable embedding API ({embedding_host}). Error in {context} {e}")
                return None
            embeddings.update(result.dense)
            percent = (i + len(batch))/no_of_items
            await bts.task_progress(task_id, percent * 100)
            logger.info(f"Embeddings: Processed {i + len(batch)}/{no_of_items} ({percent}%)")
        return embeddings


def _build_text_rows(chunk_map: Dict[str, dict]) -> List[dict]:
    return [
        {
            FlatText.ID: chunk_id,
            FlatText.PARENT_ID: entry['parent_id'],
            FlatText.OBSERVATION_ID: entry['observation_id'],
            FlatText.TEXT: entry['text'],
            FlatText.TAGS: [],
            FlatText.REQUIRE_NER: False,
            FlatText.CHUNKED: True,
            FlatText.MODEL: entry['model'],
            FlatText.TS: entry['ts'],
        }
        for chunk_id, entry in chunk_map.items()
        if entry['has_siblings']
    ]


def _build_vector_rows(chunk_map: Dict[str, dict], embeddings: Dict[str, List[float]],
                       model: str) -> List[dict]:
    rows = []
    if not embeddings:
        logger.warning(f"Embeddings not available.")
        return []

    for chunk_id in chunk_map:
        if chunk_id not in embeddings:
            logger.warning(f"No embedding returned for chunk {chunk_id}, skipping")
            continue
        rows.append({
            FlatTextVector.TEXT_ID: chunk_id,
            FlatTextVector.VECTOR: embeddings[chunk_id],
            FlatTextVector.MODEL: model,
        })
    return rows


async def _stream_in_bulks(rows: list, stream_fn, label: str, context,
                           bulk_size: int = BULK_SIZE):
    for i in range(0, len(rows), bulk_size):
        bulk = rows[i:i + bulk_size]
        start = time()
        status, total_rows, saved_rows, message = await stream_fn(bulk)
        elapsed = time() - start
        logger.stat(
            f"{label}: Saved={saved_rows}/{total_rows}, "
            f"Time={elapsed:.3f}s, "
            f"Context={context.tenant}/{context.production}")


async def chunk_texts(context):
    if not embedding_host:
        logger.info("Embedding disabled. Set EMBEDDING_HOST env var.")
        return

    count = await bd_text_adapter.count_texts_to_chunk()
    logger.info(f"There are {count} texts to chunk")
    if count == 0:
        return
    async with background_log("Chunking Worker", f"Chunking in {context}") as (bts, task_id):

        data = await bd_text_adapter.load_texts_to_chunk()
        chunker = get_text_chunker(512)
        emb_client = EmbeddingApiClient(embedding_host, embedding_api_key)
        model = 'intfloat/multilingual-e5-base'

        chunk_map, original_ids = _collect_all_chunks(data, chunker, model, now_in_utc())
        logger.info(f"Produced {len(chunk_map)} chunks from {len(original_ids)} texts")

        await bts.task_progress(task_id, 10)
        embeddings = await _embed_in_batches(chunk_map, emb_client)
        if not embeddings:
            logger.warning("No embeddings returned. Skipping...")
            return

        await bts.task_progress(task_id, 50)


        text_rows = list(map_to_table_columns(_build_text_rows(chunk_map), mapping=_sys_text_mapping))
        vector_rows = list(map_to_table_columns(_build_vector_rows(chunk_map, embeddings, model), mapping=_sys_text_vector_mapping))

        if text_rows:
            await _stream_in_bulks(text_rows, bd_text_adapter.stream, "Chunk Texts", context)
        await bts.task_progress(task_id, 60)

        if vector_rows:
            await _stream_in_bulks(vector_rows, bd_text_vector_adapter.stream, "Chunk Vectors", context)
        await bts.task_progress(task_id, 90)

        BULK_UPDATES = 250
        for i in range(0, len(original_ids), BULK_UPDATES):
            await bd_text_adapter.update_chunked_many(original_ids[i:i + BULK_UPDATES])

        await bts.task_progress(task_id, 100)
        logger.info(f"Marked {len(original_ids)} texts as chunked")


