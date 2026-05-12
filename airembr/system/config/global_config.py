import os

from airembr.system.logging.log_handler import get_logger
from airembr.system.config.sys_config import sys_config
from airembr.core.env.validator import get_env_as_int, get_env_as_bool

logger = get_logger(__name__)


class Settings:
    def __init__(self, env):
        self.pulsar_host = env.get('PULSAR_HOST', 'pulsar://localhost:6650')  # pulsar://localhost:6650
        self.pulsar_api = env.get('PULSAR_API', 'http://localhost:8080')
        self.pulsar_auth_token = env.get('PULSAR_AUTH_TOKEN', None)
        self.pulsar_topic_type = env.get('PULSAR_TOPIC_TYPE', 'persistent')
        self.pulsar_tenant = env.get('PULSAR_TENANT', f'tracardi-{sys_config.version.version}')
        self.pulsar_cluster = env.get('PULSAR_CLUSTER', 'standalone')

        self.pulsar_system_namespace = env.get('PULSAR_SYSTEM_NAMESPACE', 'system')
        self.pulsar_function_topic = env.get('PULSAR_FUNCTION_TOPIC', 'functions')
        self.pulsar_collector_topic = env.get('PULSAR_COLLECTOR_TOPIC', 'collectors')
        self.pulsar_workflow_topic = env.get('PULSAR_WORKFLOW_TOPIC', 'workflows')
        self.pulsar_destination_topic = env.get('PULSAR_DESTINATION_TOPIC', 'destinations')
        self.pulsar_log_topic = env.get('PULSAR_LOG_TOPIC', 'logs')

        self.pulsar_storage_pool = get_env_as_int('PULSAR_COLLECTOR_POOL', 1000)
        self.pulsar_serializer = env.get('PULSAR_SERIALIZER', 'json')

        self.enable_prometheus = get_env_as_bool('ENABLE_PROMETHEUS', 'no')
        self.prometheus_gateway = env.get('PROMETHEUS_GATEWAY', None)

        self.entity_cache_ttl = get_env_as_int('ENTITY_CACHE_TTL', 60 * 60)  # 1h

        if self.pulsar_host and not self.pulsar_host.startswith('pulsar://'):
            raise ValueError("PULSAR_HOST should start with pulsar://")

        if self.pulsar_host is None:
            logger.error('PULSAR_HOST is not set. Can not store data without pulsar.')
            exit(1)

        self.audience_estimation_max_cardinality_count = get_env_as_int('AUDIENCE_ESTIMATION_MAX_CARDINALITY_COUNT',
                                                                        100000)

        self.queue_adapter = env.get('QUEUE_ADAPTER', 'kafka')

        self.move_events_on_merge = get_env_as_bool('MOVE_EVENTS_ON_MERGE', 'yes')
        self.disable_consistency_check = get_env_as_bool('DISABLE_CONSISTENCY_CHECK', 'no')

        self.eff_late_profile_binding = get_env_as_bool('EFF_LATE_PROFILE_BINDING', 'yes')

        system_events_for_property_change = env.get('SYSTEM_EVENTS_FOR_PROPERTY_CHANGE', None)
        if isinstance(system_events_for_property_change, str):
            self.system_events_for_property_change = system_events_for_property_change.split(',')
        else:
            self.system_events_for_property_change = []

global_settings = Settings(os.environ)
