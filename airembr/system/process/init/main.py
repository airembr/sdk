import asyncio
from time import sleep

from airembr.system.config.global_config import global_settings
from airembr.system.process.logging.log_handler import get_logger
from airembr.core.env.validator import get_env_as_bool, get_env_as_int
from airembr.system.config.sys_config import sys_config


async def run_setup():
    logger = get_logger(__name__)

    print(
"""
██████\           ██\   ██\     
\_██  _|          \__|  ██ |    
  ██ |  ███████\  ██\ ██████\   
  ██ |  ██  __██\ ██ |\_██  _|  
  ██ |  ██ |  ██ |██ |  ██ |    
  ██ |  ██ |  ██ |██ |  ██ |██\ 
██████\ ██ |  ██ |██ |  \████  |
\______|\__|  \__|\__|   \____/ """,flush=True)

    logger.info(f"Selected queue adapter: {global_settings.queue_adapter}")

    max_retries = get_env_as_int('MAX_RETRIES', 5)

    if get_env_as_bool('QUEUE_ENABLED', 'yes'):

        if global_settings.queue_adapter == 'pulsar':
            from airembr.system.process.init.service.pulsar_set_up import PulsarSetup
            from pararun_adapter.pulsar.config import PulsarConfig

            pulsar_config = PulsarConfig()

            for t in range(0, max_retries):
                logger.dev_info(f"[QUEUE] Connecting... try: {t} out of {max_retries}")
                try:
                    pulsar = PulsarSetup(
                        broker_host=pulsar_config.pulsar_host,
                        service_host=pulsar_config.pulsar_api,
                        token=pulsar_config.pulsar_auth_token
                    )

                    await pulsar.auto_setup(sys_config.queue_tenant)
                    clusters = [cluster async for cluster in pulsar.client.list_clusters()]
                    logger.debug(f"Pulsar clusters {clusters}")
                    tenants = [tenant async for tenant in pulsar.client.list_tenants()]
                    logger.debug(f"Pulsar tenants {tenants}")
                    namespaces = [namespace async for namespace in
                                  pulsar.client.list_namespaces(sys_config.queue_tenant)]
                    logger.debug(f"Pulsar namespaces {namespaces}")
                    exit(0)
                except Exception as e:
                    logger.error(str(e))
                    sleep(10)

            exit(1)
        elif global_settings.queue_adapter == 'kafka':
            from airembr.system.process.init.service.kafka_set_up import KafkaSetup
            from pararun_adapter.kafka.config import kafka_settings
            logger.dev_info(f"[QUEUE] KAFKA_SERVERS: {kafka_settings.kafka_servers}")
            logger.dev_info(f"[QUEUE] KAFKA_SECURITY_PROTOCOL: {kafka_settings.kafka_security_protocol}")
            logger.dev_info(f"[QUEUE] KAFKA_SASL_MECHANISM: {kafka_settings.kafka_sasl_mechanism}")
            logger.dev_info(f"[QUEUE] KAFKA_BACK_PRESSURE: {kafka_settings.kafka_back_pressure}")
            logger.dev_info(f"[QUEUE] KAFKA_SASL_USERNAME: {kafka_settings.kafka_sasl_plain_username}")
            logger.dev_info(f"[QUEUE] KAFKA_SASL_PASSWORD: {kafka_settings.kafka_sasl_plain_password}")

            for t in range(0, max_retries):
                logger.dev_info(f"[QUEUE] Connecting... try: {t} out of {max_retries}")
                try:
                    kafka_setup = KafkaSetup()
                    kafka_setup.auto_setup()
                    exit(0)
                except Exception as e:
                    logger.error(str(e))
                    sleep(10)
            exit(1)

        else:
            raise ValueError(f"Unknown queue adapter: {global_settings.queue_adapter}")


asyncio.run(run_setup())
