import os

from sdk.defer.service.environment import get_env_as_int
from sdk.defer.service.logger.log_handler import get_logger
from sdk.defer.service.singleton import Singleton

logger = get_logger(__name__)

class PulsarConfig(metaclass=Singleton):
    def __init__(self):
        env = os.environ
        self.pulsar_host = env.get('PULSAR_HOST', 'pulsar://localhost:6650')  # pulsar://localhost:6650
        self.pulsar_api = env.get('PULSAR_API', 'http://localhost:8080')
        self.pulsar_auth_token = env.get('PULSAR_AUTH_TOKEN', None)
        self.pulsar_cluster = env.get('PULSAR_CLUSTER', 'standalone')

        self.pulsar_storage_pool = (
            get_env_as_int('PULSAR_COLLECTOR_POOL', 1000))
        self.pulsar_serializer = env.get('PULSAR_SERIALIZER', 'json')

        if self.pulsar_host and not self.pulsar_host.startswith('pulsar://'):
            raise ValueError("PULSAR_HOST should start with pulsar://")

        if self.pulsar_host is None:
            logger.error('PULSAR_HOST is not set. Can not store data without pulsar.')
            exit(1)
