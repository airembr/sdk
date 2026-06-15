import os
import asyncio

from pararun.consumer.executor import WorkManager

from airembr.system.service.bg.worker.process.logging import logging
from airembr.system.service.bg.worker.process.metrics import MetricsAdapter
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.config.global_config import global_settings
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.system.adapter.settings.global_settings_service import GlobalSettingsBroadcaster

logger = get_logger(__name__)


async def worker():
    consumer_adapter = os.environ.get("CONSUMER_TYPE", None)
    _adapter = queue_adapter(consumer_adapter)
    prefix = f"airembr_{_adapter.name.replace('.', '_')}"
    await WorkManager().start_worker(
        inactivity_time_out=1000,
        log_processor=logging,
        adapter=_adapter,
        metrics=MetricsAdapter(prefix)
    )


print(
    """
     ██████\                      ██\      ██\                     ██\                           
    ██  __██\                     ██ | █\  ██ |                    ██ |                          
    ██ /  \__|██\   ██\  ███████\ ██ |███\ ██ | ██████\   ██████\  ██ |  ██\  ██████\   ██████\  
    \██████\  ██ |  ██ |██  _____|██ ██ ██\██ |██  __██\ ██  __██\ ██ | ██  |██  __██\ ██  __██\ 
     \____██\ ██ |  ██ |\██████\  ████  _████ |██ /  ██ |██ |  \__|██████  / ████████ |██ |  \__|
    ██\   ██ |██ |  ██ | \____██\ ███  / \███ |██ |  ██ |██ |      ██  _██<  ██   ____|██ |      
    \██████  |\███████ |███████  |██  /   \██ |\██████  |██ |      ██ | \██\ \███████\ ██ |      
     \______/  \____██ |\_______/ \__/     \__| \______/ \__|      \__|  \__| \_______|\__|      
              ██\   ██ |                                                                         
              \██████  |                                                                         
               \______/                                                                          
    """, flush=True
)
bs = GlobalSettingsBroadcaster()
bs.start_background_listener()
logger.info("Starting Cluster Settings Broadcaster...")
logger.info(f"Monitoring enabled: {global_settings.enable_prometheus}")
logger.dev_info(f"[DEPENDENCY] QUEUE_ADAPTER: {global_settings.queue_adapter}")
if global_settings.queue_adapter == 'kafka':
    from pararun_adapter.kafka.config import kafka_settings

    logger.dev_info(f"[QUEUE] KAFKA_SERVERS: {kafka_settings.kafka_servers}")
    logger.dev_info(f"[QUEUE] KAFKA_SECURITY_PROTOCOL: {kafka_settings.kafka_security_protocol}")
    logger.dev_info(f"[QUEUE] KAFKA_SASL_MECHANISM: {kafka_settings.kafka_sasl_mechanism}")
    logger.dev_info(f"[QUEUE] KAFKA_BACK_PRESSURE: {kafka_settings.kafka_back_pressure}")
elif global_settings.queue_adapter == 'pulsar':
    from pararun_adapter.pulsar.config import pulsar_settings

    logger.dev_info(f"[QUEUE] PULSAR_HOST: {pulsar_settings.pulsar_host}")
    logger.dev_info(f"[QUEUE] PULSAR_API: {pulsar_settings.pulsar_api}")

asyncio.run(worker())
