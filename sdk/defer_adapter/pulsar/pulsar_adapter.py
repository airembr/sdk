from typing import Callable

from sdk.defer.error.client_timeout import PushError
from sdk.defer.model.worker_capsule import PublishPayload
from sdk.defer.model.data_bus import DataBus
from sdk.defer.protocol.queue_client_protocol import QueueProtocol
from .client.pulsar_client import PulsarClient, send_async_message
from .client.pulsar_subscriber_factory import topic_subscriber_factory
from .client.pulsar_producer_factory import topic_producer_factory
from .config import PulsarConfig
from .pulsar_consumer_adapter import PulsarConsumerAdapter


class PulsarAdapter(QueueProtocol):

    def __init__(self, data_bus: DataBus):
        config = PulsarConfig()
        self._client = PulsarClient(config.pulsar_host, config.pulsar_auth_token)
        self._data_bus = data_bus

    def consumer(self) -> PulsarConsumerAdapter:
        pulsar_consumer = topic_subscriber_factory(
            self._client,
            self._data_bus.topic,
            **self._data_bus.get_subscription_settings_as_dict()
        )
        return PulsarConsumerAdapter(pulsar_consumer)

    def publish(self, payload: PublishPayload, on_error: Callable):

        message, schema = self._data_bus.factory.serialize(
            payload.capsule,
            payload.job_tag,
            payload.context
        )

        # Publish, use cache to get producer
        producer = topic_producer_factory(self._client, self._data_bus.topic, schema)

        try:
            return send_async_message(
                producer,
                message=message,
                payload=payload,
                on_error=on_error
            )
        except Exception as e:
            raise PushError(str(e))

    def data_bus(self):
        return self._data_bus
