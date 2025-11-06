from typing import Tuple, Optional

from pulsar import ConsumerType, InitialPosition
from pulsar.schema import String, Record, Float, Schema, JsonSchema

from pararun_adapter.pulsar.pulsar_topics import pulsar_topics
from pararun.model.data_bus import DataBus, DataBusSubscription
from pararun.model.transport_context import TransportContext
from pararun.protocol.model_factory_protocol import SerializerProtocol
from pararun.service.logger.log_handler import now_in_utc
from pararun.transport.serializers import PickleSerializer

_default_serializer = PickleSerializer


class FunctionRecord(Record):
    """
    This is the data record that will be stored in pulsar.
    """

    timestamp = Float()
    type = String()
    name = String()
    module = String()
    args = String()
    kwargs = String()
    context = String()

    def __repr__(self):
        return f"FunctionRecord(name={self.name}, module={self.module}, args={self.args})"


# This is the Transport Schema that we will use


class FunctionSerializer(SerializerProtocol):

    def __init__(self, schema=None):
        self._schema = schema

    def schema(self):
        return self._schema

    def serialize(self, data, job_tag: str, context: TransportContext) -> Tuple[FunctionRecord, Schema]:
        context_dict = context.model_dump()

        args = _default_serializer.serialize(data.args) if data.args else ""
        kwargs = _default_serializer.serialize(data.kwargs) if data.kwargs else ""

        return FunctionRecord(
            timestamp=now_in_utc().timestamp(),
            type=job_tag,
            name=data.function.name,
            module=data.function.module,
            args=args,
            kwargs=kwargs,
            context=_default_serializer.serialize(context_dict)
        ), self._schema

    def deserialize(self, record: FunctionRecord) -> Tuple[tuple, dict, dict]:
        args = _default_serializer.deserialize(record.args) if record.args else tuple()
        kwargs = _default_serializer.deserialize(record.kwargs) if record.kwargs else {}
        context = _default_serializer.deserialize(record.context)
        return args, kwargs, context


def function_data_bus(queue_tenant: str):
    return DataBus(
        topic=pulsar_topics.system_function_topic(queue_tenant),  # system/functions
        factory=FunctionSerializer(schema=JsonSchema(FunctionRecord)),
        subscription=DataBusSubscription(
            subscription_name="background-worker",
            consumer_name="background",
            consumer_type=ConsumerType.Shared,
            initial_position=InitialPosition.Earliest,
            receiver_queue_size=2500
        )
    )
