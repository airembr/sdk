import os

from sdk.defer.service.environment import get_env_as_bool, get_env_as_int
from sdk.defer.service.logger.log_handler import get_logger
from sdk.defer.service.singleton import Singleton

logger = get_logger(__name__)


class KafkaConfig(metaclass=Singleton):
    def __init__(self, env):
        self.kafka_servers = env.get('KAFKA_SERVERS', 'localhost:9093').split(',')
        self.kafka_security_protocol = env.get('KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT')
        self.kafka_sasl_mechanism = env.get('KAFKA_SASL_MECHANISM', 'PLAIN')

        self.kafka_sasl_plain_username = env.get('KAFKA_SASL_PLAIN_USERNAME', None)
        self.kafka_sasl_plain_password = env.get('KAFKA_SASL_PLAIN_PASSWORD', None)
        self.kafka_metadata_max_age_ms = get_env_as_int('KAFKA_METADATA_MAX_AGE_MS', 300000)
        self.kafka_request_timeout_ms = get_env_as_int('KAFKA_REQUEST_TIMEOUT_MS', 40000)
        self.kafka_max_batch_size = get_env_as_int('KAFKA_MAX_BATCH_SIZE', 16384)
        self.kafka_max_request_size = get_env_as_int('KAFKA_MAX_REQUEST_SIZE', 1048576)

        self.kafka_ca_cert = env.get('KAFKA_CA_CERT', None)
        self.kafka_certfile = env.get('KAFKA_CERTFILE', None)
        self.kafka_keyfile = env.get('KAFKA_KEY_FILE', None)
        # self.kafka_tenant = env.get('KAFKA_TENANT', None)

        if self.kafka_servers is None:
            logger.error('KAFKA_SERVERS is not set. Can not store data without pulsar.')
            exit(1)

        if self.kafka_servers and not isinstance(self.kafka_servers, list):
            raise ValueError("KAFKA_SERVERS should be set and a list of coma separated values.")

        # if self.kafka_tenant is None:
        #     logger.error('KAFKA_TENANT is not set. Can not store data without pulsar tenant.')
        #     exit(1)

kafka_settings = KafkaConfig(os.environ)