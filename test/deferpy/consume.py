import asyncio
from sdk.defer.consumer.executor import start_worker, get_consumer_adapter
from sdk.defer.model.transport_context import TransportContext
from sdk.defer.service.logger.log_handler import DeferLogHandler
from sdk.defer_adapter import queue_type
from test.deferpy.worker import run_function


async def save_logs(handler: DeferLogHandler, context: TransportContext):
    print(handler.collection)


async def worker():
    queue_tenant = "airembr-0.0.1"
    await start_worker(
        inactivity_time_out=3000,
        log_processor=save_logs,
        adapter=get_consumer_adapter(
            queue_tenant,
            "new-subscription-3",  # New subscription consumes all messages from the begining
            "new-consumer-1",  # New consumer is a new worker
            queue_type.FUNCTION,
            run_function,  # Signature of function: (transport_context: TransportContext, data)
            (
                None,
                None,
                0,  # min size
                0,  # Max size
                0  # timeout
            )
        )
    )


if __name__ == "__main__":
    asyncio.run(worker())
