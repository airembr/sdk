import asyncio
import os
from asyncio import sleep
from time import time

from srd.config import StarRocksConfig
from airembr.model.system.context import ServerContext
from airembr.system.process.ai.chunker.text_chunk_embedder import chunk_texts
from airembr.system.process.stitching.stitch import stitch
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.adapter.bigdata.tenant.tenant_adapter import load_tenant_database_and_context

logger = get_logger(__file__)


async def main():
    t = time()

    config = StarRocksConfig()

    logger.info(
        f"Config: starrocks_database_uri = {config.starrocks_database_uri} (env: {os.environ.get('STARROCKS_HOST', None)})")

    # Scan database names and produce context
    async for database, context in load_tenant_database_and_context():
        logger.info(f"Context: {context}, Database: {database}")
        with ServerContext(context):
            await asyncio.gather(
                stitch(context, database),
                chunk_texts(context),
            )

            # await chunk_texts(context)

            # # logger.info("Text summarization...")
            # # await summarize(context)
            # #
            # # # Embed texts
            # # logger.info("Text embeddings...")
            # await embed(context)
            #
            # # Stitch entity state
            # await stitch(context, database)
            #
            # # Embed texts
            # # logger.info("Text entities...")
            # await extract_entities(context)
            # #
            # # # Stitch entity state
            # # await stitch(context, database)
            # #
            # # # Embedd again
            # # # logger.info("Text embeddings...")
            # # await embed(context)

    await sleep(2)

    logger.info(f"Finished in {time() - t}")


asyncio.run(main())
