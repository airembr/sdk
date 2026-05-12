from typing import List

from pararun.model.batcher import BatcherConfig
from pararun.model.transport_context import TransportContext
from pararun.publisher.deferer import deferred_execution
from pararun_adapter import queue_type

from airembr.model.system.job_tags import LOG_STORAGE_TAG
from airembr.model.system.context import Context, ServerContext, get_context
from airembr.system.config.log_config import logging_config
from airembr.system.logging.log_handler import get_installation_logger
from airembr.system.adapter.queue.queue_adapter import queue_adapter

from system.adapter.bigdata.big_data_adapter import *

logger = get_installation_logger(__name__)


async def batch_save_logs(context: TransportContext, batch: List[dict]):
    # Will run or be queued only when logger_guard return True.
    with ServerContext(Context(**context.as_context())):
        await bd_log_adapter.save_logs(batch)


def logger_guard(context: TransportContext, logs: List[dict]):
    return bool(logs)


def single_log_collector_in_queue(context: TransportContext, logs: List[dict]):
    return logs


async def log_saver_worker(logs: list):
    if logging_config.save_logs:
        context = get_context()
        transport_context = TransportContext.build(context)
        # Queue
        if context.get_headers().should_queue('log'):
            with deferred_execution(guard=logger_guard) as defer:
                status = await defer(single_log_collector_in_queue)(logs).push(
                    LOG_STORAGE_TAG,
                    transport_context,
                    batcher=BatcherConfig(
                        func=batch_save_logs,
                        min_size=500,
                        max_size=1000,
                        timeout=30
                    ),
                    adapter=queue_adapter(queue_type.LOGGER)
                )

                if status.error:
                    await batch_save_logs(transport_context, batch=logs)

        # not-queue
        else:
            await batch_save_logs(transport_context, batch=logs)
