from pulsar import ConsumerType, InitialPosition
from pulsar.schema import JsonSchema

from pararun_adapter.pulsar.pulsar_topics import pulsar_topics
from pararun.model.data_bus import DataBus, DataBusSubscription

from pararun_adapter.pulsar.bus.pulsar_data_bus import FunctionSerializer, FunctionRecord
from pararun.transport.serializers import PickleSerializer

_default_serializer = PickleSerializer


# This is the definition of DataBus that configs the subscriber, schema and topic.

def destination_data_bus(queue_tenant:str):
    return DataBus(
        topic=pulsar_topics.destination_function_topic(queue_tenant),  # system/destinations
        factory=FunctionSerializer(schema=JsonSchema(FunctionRecord)),
        subscription=DataBusSubscription(
            subscription_name="destination",
            consumer_name="destination",
            consumer_type=ConsumerType.Shared,
            initial_position=InitialPosition.Earliest,
            receiver_queue_size=1000
        )
    )
