import os
import asyncio

from sdk.defer.consumer.executor import start_worker
from sdk.defer.model.transport_context import TransportContext
from sdk.defer.service.logger.log_handler import DeferLogHandler
from sdk.defer_adapter import queue_type
from sdk.defer_adapter.adaper_selector import DeferAdapterSelector

def run_function(context, param):
    print('run')

async def save_logs(handler: DeferLogHandler, context: TransportContext):
    print(handler.collection)

def get_adapter():
    consumer_adapter = queue_type.FUNCTION
    queue_tenant = "airembr-0.0.1"
    adapter = DeferAdapterSelector().get(consumer_adapter, queue_tenant)

    # adapter.init_function = (
    #     "bg.wk.ai.embeddings.main",
    #     "init"
    # )
    adapter.override_function = (
        "test.deferpy.consume",
        "run_function"
    )
    adapter.override_batcher = (
        None,
        None,
        0,  # min size
        0,  # Max size
        0  # timeout
    )
    # adapter.override_batcher = (
    #     "bg.wk.ai.embeddings.main",
    #     "ai_embeddings_bulk_consumer",
    #     0,  # min size
    #     500,  # Max size
    #     15  # timeout
    # )
    return adapter

async def worker():

    await start_worker(
        inactivity_time_out=3000,
        log_processor=save_logs,
        adapter=get_adapter()
    )

asyncio.run(worker())
