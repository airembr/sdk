from pulsar import ConsumerType, InitialPosition
from pulsar.schema import JsonSchema

from sdk.defer_adapter.pulsar.pulsar_topics import pulsar_topics
from sdk.defer_adapter.pulsar.bus.pulsar_data_bus import FunctionSerializer, FunctionRecord

from sdk.defer.model.data_bus import DataBus, DataBusSubscription
from sdk.defer.transport.serializers import PickleSerializer

_default_serializer = PickleSerializer


# This is the definition of DataBus that configs the subscriber, schema and topic.

def logger_data_bus(queue_tenant:str):
    return DataBus(
        topic=pulsar_topics.logger_function_topic(queue_tenant),  # system/logs
        factory=FunctionSerializer(schema=JsonSchema(FunctionRecord)),
        subscription=DataBusSubscription(
            subscription_name="log",
            consumer_name="log",
            consumer_type=ConsumerType.Shared,
            initial_position=InitialPosition.Earliest,
            receiver_queue_size=1000
        )
    )
