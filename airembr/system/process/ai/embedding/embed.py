from airembr.system.process.logging.log_handler import get_logger
from airembr.sdk.service.remote.embedding_api_client import EmbeddingApiClient
from airembr.sdk.ai.config import embedding_host, embedding_api_key
from airembr.core.data.chunker import chunk_generator
from airembr.system.adapter.bigdata.big_data_adapter import bd_text_adapter, bd_entity_property_adapter, \
    bd_text_vector_adapter

logger = get_logger(__name__)

def _update_vectors(model, vectors):
    for text_id,vector in vectors.items():
        record = {}
        record['text_id'] = text_id
        record['model'] = model
        record["vector"] = vector
        yield record

async def embed(context):

    if not embedding_host:
        logger.info("Embedding is disabled. Please set EMBEDDING_HOST and EMBEDDING_API_KEY environment variables.")
        return

    count = await bd_text_adapter.count_not_embedded_tests()
    logger.info(f"There are {count} texts to embed...")

    model = 'intfloat/multilingual-e5-base'
    rows = await bd_text_adapter.load_not_embedded_tests()

    emb_client = EmbeddingApiClient(embedding_host, embedding_api_key)
    for batch in chunk_generator(rows, batch_size=500, proceed_if=True):
        batch = list(batch)
        logger.info(f"Embedding {len(batch)} texts.")
        text_dict = {row['id']: row['text_string'] for row in batch}
        text_embeddings = emb_client.call(text_dict).get_mapped_embeddings()
        updated_rows = list(_update_vectors(model, text_embeddings.dense))
        await bd_text_vector_adapter.stream(updated_rows)

    # Embed property values
    count = await bd_entity_property_adapter.count_not_embedded_property_values()
    logger.info(f"There are {count} property values to embed...")

    rows = await bd_entity_property_adapter.load_not_embedded_property_values()
    for batch in chunk_generator(rows, batch_size=500, proceed_if=True):
        batch = list(batch)
        logger.info(f"Embedding {len(batch)} property values.")
        text_dict = {row['id']: row['text_string'] for row in batch}
        text_embeddings = emb_client.call(text_dict).get_mapped_embeddings()
        updated_rows = list(_update_vectors(model, text_embeddings.dense))
        await bd_text_vector_adapter.stream(updated_rows)
