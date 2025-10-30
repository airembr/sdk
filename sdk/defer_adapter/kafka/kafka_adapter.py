import json
from typing import Callable
from sdk.defer.model.data_bus import DataBus
from sdk.defer.model.worker_capsule import PublishPayload
from sdk.defer.protocol.queue_client_protocol import QueueProtocol

from sdk.defer_adapter.kafka.client.kafka_client import KafkaClient
from sdk.defer_adapter.kafka.config import kafka_settings
from sdk.defer_adapter.kafka.kafka_consumer_adapter import KafkaConsumerAdapter

_serializer = lambda v: json.dumps(v).encode('utf-8')
_deserializer = lambda x: json.loads(x.decode('utf-8'))


class KafkaAdapter(QueueProtocol):

    def __init__(self, data_bus: DataBus):
        self._client = KafkaClient(kafka_settings)
        self._producer = self._client.get_producer(serializer=_serializer)
        self._data_bus = data_bus

    def consumer(self) -> KafkaConsumerAdapter:
        consumer = self._client.get_consumer(
            topic=self._data_bus.topic,
            group_id=self._data_bus.subscription.subscription_name,  # Consumer group
            client_id=self._data_bus.subscription.consumer_name,
            deserializer=_deserializer,
            auto_offset_reset=self._data_bus.subscription.initial_position
        )

        return KafkaConsumerAdapter(consumer)

    def publish(self, payload: PublishPayload, on_error: Callable):
        # Serialize record - it creates an object - serialization is in producer
        record, schema = self._data_bus.factory.serialize(payload.capsule, payload.job_tag, payload.context)

        # Convert headers
        headers = [(key, value.encode('utf-8')) for key, value in payload.headers.items()]

        try:
            return self._producer.send(self._data_bus.topic, value=record, headers=headers)
        except Exception as e:
            on_error(payload)

    def data_bus(self):
        return self._data_bus

    def __del__(self):
        if self._producer:
            self._producer.close()
