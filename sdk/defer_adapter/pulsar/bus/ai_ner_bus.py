from pulsar import ConsumerType, InitialPosition
from pulsar.schema import JsonSchema

from sdk.defer_adapter.pulsar.pulsar_topics import pulsar_topics
from sdk.defer.model.data_bus import DataBus, DataBusSubscription

from sdk.defer_adapter.pulsar.bus.pulsar_data_bus import FunctionSerializer, FunctionRecord
from sdk.defer.transport.serializers import PickleSerializer

_default_serializer = PickleSerializer


# This is the definition of DataBus that configs the subscriber, schema and topic.

def ai_ner_bus(queue_tenant:str):
    return DataBus(
        topic=pulsar_topics.ai_ner_topic(queue_tenant),  # system/ai_ner
        factory=FunctionSerializer(schema=JsonSchema(FunctionRecord)),
        subscription=DataBusSubscription(
            subscription_name="AI NER",
            consumer_name="AI NER CONSUMER",
            consumer_type=ConsumerType.Shared,
            initial_position=InitialPosition.Earliest,
            receiver_queue_size=1000
        )
    )
