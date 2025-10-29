import os
from typing import Optional

from pulsar.schema import JsonSchema

from sdk.defer.model.adapter import Adapter
from sdk.defer_adapter.kafka.bus.kafka_data_bus import KafkaFunctionSerializer, kafka_data_bus
from sdk.defer_adapter.kafka.kafka_adapter import KafkaAdapter
from sdk.defer_adapter.pulsar.bus.event_attachment_data_bus import event_attachment_bus
from sdk.defer_adapter.pulsar.bus.destination_data_bus import destination_data_bus
from sdk.defer_adapter.pulsar.bus.observation_payload_bus import collector_json_bus, ObservationSerializer, \
    ObservationRecord
from sdk.defer_adapter.pulsar.bus.logger_data_bus import logger_data_bus
from sdk.defer_adapter.pulsar.bus.pulsar_data_bus import FunctionSerializer, FunctionRecord, function_data_bus
from sdk.defer_adapter.pulsar.bus.workflow_data_bus import workflow_data_bus
from sdk.defer_adapter.pulsar.pulsar_adapter import PulsarAdapter

from sdk.defer_adapter.run_once import run_once

_queue_adapter_var = os.environ.get('QUEUE_ADAPTER', 'pulsar')


@run_once
def collector_queue_adapter(queue_tenant: Optional[str] = None) -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':

        _adapter = Adapter(
            # TODO This is also available in collector_data_bus - could be removed
            serializers={
                "ObservationSerializer": ObservationSerializer(schema=JsonSchema(ObservationRecord)),
            },
            adapter_protocol=PulsarAdapter(
                collector_json_bus(
                    'event-collector-worker',
                    'event-collector',
                    queue_tenant)
            )
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def function_queue_adapter(queue_tenant: Optional[str] = None) -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':
        _adapter = Adapter(
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            adapter_protocol=PulsarAdapter(function_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def workflow_queue_adapter(queue_tenant: Optional[str] = None) -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':
        _adapter = Adapter(
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            adapter_protocol=PulsarAdapter(workflow_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def destination_queue_adapter(queue_tenant: Optional[str] = None) -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':
        _adapter = Adapter(
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            # Add data bus
            adapter_protocol=PulsarAdapter(destination_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def logger_queue_adapter(queue_tenant: Optional[str] = None) -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':
        _adapter = Adapter(
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            # Add data bus
            adapter_protocol=PulsarAdapter(logger_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def event_property_queue_adapter(queue_tenant: Optional[str] = None) -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':

        _adapter = Adapter(
            # TODO This is also available in collector_data_bus - could be removed
            serializers={
                # "TrackerPayloadSerializer": TrackerPayloadSerializer(schema=JsonSchema(FunctionRecord)),
                "ObservationSerializer": ObservationSerializer(schema=JsonSchema(FunctionRecord)),
            },
            adapter_protocol=PulsarAdapter(
                collector_json_bus(
                    'event-property-worker',
                    'event-property',
                    queue_tenant)
            )
        )

    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


# Consumer only
@run_once
def event_property_adapter(queue_tenant: Optional[str] = None):
    event_property_consumer = event_property_queue_adapter(queue_tenant)
    event_property_consumer.override_function = (
        "bg.wk.background.consumer.properties.main", "event_property_consumer")
    event_property_consumer.override_batcher = (None, None, 0, 0, 0)  # Reset to no bulker
    return event_property_consumer


@run_once
def event_attachment_adapter(queue_tenant: Optional[str] = None) -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':

        _adapter = Adapter(
            # TODO This is also available in collector_data_bus - could be removed
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            adapter_protocol=PulsarAdapter(event_attachment_bus(queue_tenant))
        )

    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus(queue_tenant))
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter

