from typing import Optional

from kafka import KafkaProducer, KafkaConsumer

from sdk.defer.service.singleton import Singleton
from sdk.defer_adapter.kafka.config import KafkaConfig


class KafkaClient(metaclass=Singleton):

    def __init__(self, kafka_settings: KafkaConfig):
        self._kafka_settings = kafka_settings

    def get_producer(self, serializer: callable) -> KafkaProducer:

        return KafkaProducer(

            bootstrap_servers=self._kafka_settings.kafka_servers,  # Replace with your Kafka server

            ssl_cafile=self._kafka_settings.kafka_ca_cert,
            ssl_certfile=self._kafka_settings.kafka_certfile,
            ssl_keyfile=self._kafka_settings.kafka_keyfile,

            security_protocol=self._kafka_settings.kafka_security_protocol,
            sasl_mechanism=self._kafka_settings.kafka_sasl_mechanism,
            sasl_plain_username=self._kafka_settings.kafka_sasl_plain_username,
            sasl_plain_password=self._kafka_settings.kafka_sasl_plain_password,

            value_serializer=serializer  # Serialize data to JSON
        )

    def get_consumer(self, topic: str, group_id: str, deserializer: callable, auto_offset_reset: str,
                     client_id: Optional[str] = None) -> KafkaConsumer:

        return KafkaConsumer(
            topic,  # Topic name

            bootstrap_servers=self._kafka_settings.kafka_servers,  # Replace with your Kafka server

            ssl_cafile=self._kafka_settings.kafka_ca_cert,
            ssl_certfile=self._kafka_settings.kafka_certfile,
            ssl_keyfile=self._kafka_settings.kafka_keyfile,

            security_protocol=self._kafka_settings.kafka_security_protocol,
            sasl_mechanism=self._kafka_settings.kafka_sasl_mechanism,
            sasl_plain_username=self._kafka_settings.kafka_sasl_plain_username,
            sasl_plain_password=self._kafka_settings.kafka_sasl_plain_password,

            auto_offset_reset=auto_offset_reset,  # Start reading from the beginning if no offset is set
            enable_auto_commit=False,  # Commit offsets automatically
            group_id=group_id,  # Consumer group
            client_id=client_id,
            value_deserializer=deserializer  # Deserialize JSON data
        )
