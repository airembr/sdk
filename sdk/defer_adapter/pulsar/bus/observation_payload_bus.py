from typing import Tuple, List, Optional

from pulsar import ConsumerType, InitialPosition
from pulsar.schema import JsonSchema, Schema, String, Record, Float

from sdk.defer_adapter.pulsar.pulsar_topics import pulsar_topics
from sdk.defer.model.data_bus import DataBus, DataBusSubscription
from sdk.defer.model.transport_context import TransportContext
from sdk.defer.model.worker_capsule import WorkerCapsule
from sdk.defer.protocol.model_factory_protocol import SerializerProtocol

from sdk.defer.service.timestamp import now_in_utc
from sdk.defer.transport.serializers import JsonSerializer

_default_serializer = JsonSerializer


class ObservationRecord(Record):
    """
    This is the data record that will be stored in pulsar.
    """

    timestamp = Float()
    type = String()
    name = String()
    module = String()

    headers = String()
    observations = String()
    context = String()

    def __repr__(self):
        return f"ObservationRecord(name={self.name}, module={self.module}, headers={self.headers}, observations={self.observations})"


# This is the Transport Schema that we will use
_schema = JsonSchema(ObservationRecord)


class ObservationSerializer(SerializerProtocol):

    def __init__(self, schema=None):
        self._schema = schema

    def schema(self):
        return self._schema

    def serialize(self, data: WorkerCapsule, event_name: str, context: TransportContext) -> Tuple[
        ObservationRecord, Schema]:
        context_dict = context.model_dump()

        if len(data.args) != 2:
            raise ValueError("Observation should have 2 args headers (as 1st) and observation object (as 2nd).")

        headers = _default_serializer.serialize(data.args[0])
        observations = _default_serializer.serialize([observation for observation in data.args[1]])

        return ObservationRecord(
            timestamp=now_in_utc().timestamp(),
            type=event_name,
            name=data.function.name,
            module=data.function.module,
            headers=headers,
            observations=observations,
            context=_default_serializer.serialize(context_dict)
        ), _schema

    def deserialize(self, record: ObservationRecord) -> Tuple[Tuple[dict, List[dict]], dict, dict]:
        headers = _default_serializer.deserialize(record.headers) if record.headers else {}
        observations = _default_serializer.deserialize(record.observations) if record.observations else []

        args = (headers, observations)

        context = _default_serializer.deserialize(record.context)

        return args, {}, context


# This is the definition of DataBus that configs the subscriber, schema and topic.

def collector_json_bus(subscription, consumer_name, queue_tenant: str):
    return DataBus(
        topic=pulsar_topics.collector_function_topic(queue_tenant),  # system/collectors
        factory=ObservationSerializer(schema=JsonSchema(ObservationRecord)),
        subscription=DataBusSubscription(
            subscription_name=subscription,
            consumer_name=consumer_name,
            consumer_type=ConsumerType.Shared,
            initial_position=InitialPosition.Earliest,
            receiver_queue_size=2500
        )
    )
