from typing import Tuple, Any

from sdk.defer.model.data_bus import DataBus, DataBusSubscription
from sdk.defer.model.transport_context import TransportContext
from sdk.defer.protocol.model_factory_protocol import SerializerProtocol
from sdk.defer.service.logger.log_handler import get_logger, now_in_utc
from sdk.defer.transport.serializers import JsonSerializer

logger = get_logger(__name__)

_default_serializer = JsonSerializer


class DefaultSerializer(SerializerProtocol):

    def __init__(self, schema=None):
        self._schema = schema

    def schema(self):
        return self._schema

    def serialize(self, data, event_name: str, context: TransportContext) -> Tuple[Any, Any]:
        context_dict = context.model_dump()

        args = data.args if data.args else []
        kwargs = data.kwargs if data.kwargs else {}

        message = dict(
            timestamp=now_in_utc().timestamp(),
            type=event_name,
            args=args,
            kwargs=kwargs,
            context=context_dict
        )

        return _default_serializer.serialize(message), None

    def deserialize(self,record: str) -> Tuple[tuple, dict, dict]:
        deserialized = _default_serializer.deserialize(record)
        return deserialized.get('args',tuple()), deserialized.get('kwargs', {}), deserialized.get('context',{})


# This is the definition of DataBus that configs the subscriber, schema and topic.
# DataBus definition must be passed to defer.push function and set in worker background_function_worker.

def get_default_data_bus(topic: str,
                         subscription_name: str,
                         consumer_name,
                         consumer_type,
                         initial_position,
                         receiver_queue_size=1000):

    return DataBus(
        topic=topic,  # system/functions
        factory=DefaultSerializer(schema=None),
        subscription=DataBusSubscription(
            subscription_name=subscription_name,
            consumer_name=consumer_name,
            consumer_type=consumer_type,
            initial_position=initial_position,
            receiver_queue_size=receiver_queue_size
        )
    )
