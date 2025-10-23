# from typing import Tuple
#
# from pulsar import ConsumerType, InitialPosition
# from pulsar.schema import JsonSchema, Schema, String, Record, Float
#
# from sdk.defer_adapter.pulsar.pulsar_topics import pulsar_topics
# from sdk.defer.model.data_bus import DataBus, DataBusSubscription
# from sdk.defer.model.transport_context import TransportContext
# from sdk.defer.protocol.model_factory_protocol import SerializerProtocol
# from sdk.defer.service.timestamp import now_in_utc
# from sdk.defer.transport.serializers import PickleSerializer
#
# _default_serializer = PickleSerializer
#
#
# class TrackerPayloadRecord(Record):
#     """
#     This is the data record that will be stored in pulsar.
#     """
#
#     timestamp = Float()
#     type = String()
#     name = String()
#     module = String()
#
#     args = String()
#     kwargs = String()
#     context = String()
#
#     def __repr__(self):
#         return f"TrackerPayloadRecord(name={self.name}, module={self.module}, args={self.args})"
#
#
# # This is the Transport Schema that we will use
# _schema = JsonSchema(TrackerPayloadRecord)
#
#
# class TrackerPayloadSerializer(SerializerProtocol):
#
#     def __init__(self, schema=None):
#         self._schema = schema
#
#     def schema(self):
#         return self._schema
#
#     def serialize(self, data, event_name: str, context: TransportContext) -> Tuple[TrackerPayloadRecord, Schema]:
#         context_dict = context.model_dump()
#
#         print(data)
#
#         args = _default_serializer.serialize(data.args) if data.args else ""
#         kwargs = _default_serializer.serialize(data.kwargs) if data.kwargs else ""
#
#         return TrackerPayloadRecord(
#             timestamp=now_in_utc().timestamp(),
#             type=event_name,
#             name=data.function.name,
#             module=data.function.module,
#             args=args,
#             kwargs=kwargs,
#             context=_default_serializer.serialize(context_dict)
#         ), _schema
#
#     def deserialize(self, record: TrackerPayloadRecord) -> Tuple[tuple, dict, dict]:
#         args = _default_serializer.deserialize(record.args) if record.args else []
#         kwargs = _default_serializer.deserialize(record.kwargs) if record.kwargs else {}
#         context = _default_serializer.deserialize(record.context)
#         return args, kwargs, context
#
#
# # This is the definition of DataBus that configs the subscriber, schema and topic.
#
# collector_data_bus = lambda subscription, consumer_name: DataBus(
#     topic=pulsar_topics.collector_function_topic,  # system/collectors
#     factory=TrackerPayloadSerializer(schema=JsonSchema(TrackerPayloadRecord)),
#     subscription=DataBusSubscription(
#         subscription_name=subscription,
#         consumer_name=consumer_name,
#         consumer_type=ConsumerType.Shared,
#         initial_position=InitialPosition.Earliest,
#         receiver_queue_size=2500
#     )
# )
