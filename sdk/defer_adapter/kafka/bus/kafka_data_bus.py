from typing import Tuple, Optional

from sdk.defer_adapter.kafka.kafka_topics import kafka_topics
from sdk.defer.model.data_bus import DataBus, DataBusSubscription
from sdk.defer.model.transport_context import TransportContext
from sdk.defer.protocol.model_factory_protocol import SerializerProtocol
from sdk.defer.service.logger.log_handler import get_logger, now_in_utc
from sdk.defer.transport.serializers import PickleSerializer

logger = get_logger(__name__)

_default_serializer = PickleSerializer


class KafkaFunctionSerializer(SerializerProtocol):

    def __init__(self, schema=None):
        self._schema = schema

    def schema(self):
        return self._schema

    def serialize(self, data, event_name: str, context: TransportContext) -> Tuple[dict, None]:

        args = _default_serializer.serialize(data.args) if data.args else ""
        kwargs = _default_serializer.serialize(data.kwargs) if data.kwargs else ""
        context_dict = _default_serializer.serialize(context.model_dump())

        message = dict(
            timestamp=now_in_utc().timestamp(),
            type=event_name,
            args=args,
            kwargs=kwargs,
            context=context_dict
        )

        # No need to serialize - kafka has def of serializer in producer
        return message, None

    def deserialize(self, record: dict) -> Tuple[tuple, dict, dict]:

        args = _default_serializer.deserialize(record.get('args')) if record.get('args') else tuple()
        kwargs = _default_serializer.deserialize(record.get('kwargs')) if record.get('kwargs') else {}
        context = _default_serializer.deserialize(record.get('context'))

        return args, kwargs, context

        # No need to deserialize - kafka has def of deserializer in consumer
        # return record.get('args', tuple()), record.get('kwargs', {}), record.get('context', {})


def kafka_data_bus(kafka_tenant: str):
    return DataBus(
        topic=kafka_topics.system_function_topic(kafka_tenant),  # system-functions,
        factory=KafkaFunctionSerializer(schema=None),
        subscription=DataBusSubscription(
            subscription_name="collector",
            consumer_name="collector",
            consumer_type=None,
            initial_position='earliest',
            receiver_queue_size=1000
        )
    )