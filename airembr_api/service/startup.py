import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from pararun_adapter import queue_type

from airembr.system.license.license_verifier import system_license
from airembr_api.service import state
from airembr.system.adapter.settings.global_settings_service import GlobalSettingsBroadcaster
from airembr.system.adapter.bigdata.big_data_adapter import *
from airembr.system.process.bootstrap.boot_redis_db import wait_for_redis_connection
from airembr.system.process.bootstrap.boot_md_db import wait_for_metadata_store
from airembr.system.process.bootstrap.boot_bd_db import wait_for_bigdata_store
from airembr.system.process.logging import extra_info
from airembr.system.process.logging.log_format_adapter import log_format_adapter
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.config.sys_config import sys_config
from airembr.system.config.mysql_config import mysql_config
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.config.global_config import global_settings
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.sdk.storage.cache.config import redis_config

from bg.job.embedder.config import embedding_host, embedding_api_key

logger = get_logger(__name__)

_log_format_adapter = log_format_adapter()

api_ready = False

def _check_required_settings():
    settings = [
        ('FAIL_OVER_SERVER_API', 'Fail-Over server not set'),
        ('FAIL_OVER_SERVER_TOKEN', 'Fail-Over server token not set.')]
    for setting, message in settings:
        if setting not in os.environ:
            logger.warning(message, extra=extra_info.build('_check_required_settings', error_number="SET-0001"))

async def app_starts():
    # Ascii Art: BigMoney Ne
    print(f"""
          ██\                                ██\                 
          \__|                               ██ |                
 ██████\       █████\ █████\   ██████\████\  ███████\   ██████\  
 \____██\ ██\ ██  __███  __██\ ██  _██  _██\ ██  __██\ ██  __██\ 
 ███████ |██ |██ |  \████████ |██ / ██ / ██ |██ |  ██ |██ |  \__|
██  __██ |██ |██ |   ██   ____|██ | ██ | ██ |██ |  ██ |██ |      
\███████ |██ |██ |   \███████\ ██ | ██ | ██ |███████  |██ |      
 \_______|\__|\__|    \_______|\__| \__| \__|\_______/ \__|""", flush=True)

    print(
        f"{str(sys_config.version)} (Tag: {sys_config.image_tag}) (Multi-Tenant: {sys_config.multi_tenant}) (Adapters: {sys_config.cache_adapter},{global_settings.queue_adapter})",
        flush=True)

    logging.getLogger("uvicorn.access").handlers[0].setFormatter(_log_format_adapter)

    logger.info(f"LICENSE: {system_license}")
    logger.info(f"Multi-tenant LICENSE: {system_license.multi_tenant}")
    logger.info(f"Waiting for metadata store at {mysql_config.mysql_host}")
    await wait_for_metadata_store()

    logger.info(f"Waiting for cache at {redis_config.redis_host}...")
    wait_for_redis_connection()

    db_type, user, host, port = bd_install_adapter.get_connection_info()
    logger.info(f"Waiting for {db_type} connection at {user}@{host}:{port}...")
    await wait_for_bigdata_store()

    if sys_config.enable_global_settings:
        bs = GlobalSettingsBroadcaster()
        bs.start_background_listener()

    logger.dev_info("Starting Cluster Settings Broadcaster...")
    logger.dev_info(f"MULTI_TENANT_MANAGER_URL:  {sys_config.multi_tenant_manager_url}.")
    logger.dev_info(f"[DEPENDENCY] LOGGING_FORMAT: {_log_format_adapter}")
    logger.dev_info(f"[DEPENDENCY] QUEUE_ADAPTER: {global_settings.queue_adapter}")
    logger.dev_info(f"[DEPENDENCY] BIG_DATA_ADAPTER: {sys_config.big_data_adapter}")
    logger.dev_info(f"[DEPENDENCY] METADATA_STORE_ADAPTER: {sys_config.meta_data_adapter}")
    logger.dev_info(f"[DEPENDENCY] CACHE_ADAPTER: {sys_config.cache_adapter}")

    if system_license.valid:
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

    logger.dev_info(f"[FEATURE] ENABLE_TRIGGERS: {sys_config.enable_triggers}")
    logger.dev_info(f"[FEATURE] ENABLE_EVENT_RESHAPING: {sys_config.enable_event_reshaping}")
    logger.dev_info(f"[FEATURE] ENABLE_EVENT_VALIDATION: {sys_config.enable_event_validation}")
    logger.dev_info(f"[FEATURE] ENABLE_EVENT_SOURCE_CHECK: {sys_config.enable_event_source_check}")
    logger.dev_info(f"[CACHE] EVENT_MAPPING_CACHE_TTL: {memory_cache_config.event_mapping_cache_ttl}")
    logger.dev_info(f"[CACHE] EVENT_RESHAPING_CACHE_TTL: {memory_cache_config.event_reshaping_cache_ttl}")
    logger.dev_info(f"[CACHE] EVENT_VALIDATION_CACHE_TTL: {memory_cache_config.event_validation_cache_ttl}")
    logger.dev_info(f"[CACHE] EVENT_TO_PROFILE_COPING_TTL: {memory_cache_config.event_to_profile_coping_ttl}")
    logger.dev_info(f"[CACHE] DESTINATION_CACHE_TTL: {memory_cache_config.destination_cache_ttl}")
    logger.dev_info(f"[CACHE] DATA_COMPLIANCE_CACHE_TTL: {memory_cache_config.data_compliance_cache_ttl}")
    logger.dev_info(f"[CACHE] IDENTIFICATION_POINTS_CACHE_TTL: {memory_cache_config.identification_points_cache_ttl}")
    logger.dev_info(f"[CACHE] EVENT_SOURCE_CACHE_TTL: {memory_cache_config.source_ttl}")

    _check_required_settings()


async def app_shutdown():
    logger.dev_info("App shut-down...")
    # Close BD connection
    await bd_install_adapter.close()
    # Any adapter will do. And we need to do it once
    queue_adapter(queue_type.COLLECTOR).adapter_protocol.close()
    # TODO Close Metadata connection


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await app_starts()
    state.server_ready = True
    embedding_configured = bool(embedding_host and embedding_api_key)
    logger.info(f"EMBEDDING server configured: {embedding_configured}")
    logger.info(f"System started successfully.")
    yield
    await app_shutdown()
