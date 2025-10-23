import os

from pulsar.schema import JsonSchema

from sdk.defer.model.adapter import Adapter
from sdk.defer_adapter.kafka.bus.kafka_data_bus import KafkaFunctionSerializer, kafka_data_bus
from sdk.defer_adapter.kafka.kafka_adapter import KafkaAdapter
from sdk.defer_adapter.pulsar.bus.ai_ner_bus import ai_ner_bus
from sdk.defer_adapter.pulsar.bus.destination_data_bus import destination_data_bus
from sdk.defer_adapter.pulsar.bus.observation_payload_bus import collector_json_bus, ObservationSerializer
from sdk.defer_adapter.pulsar.bus.logger_data_bus import logger_data_bus
from sdk.defer_adapter.pulsar.bus.pulsar_data_bus import FunctionSerializer, FunctionRecord, function_data_bus
from sdk.defer_adapter.pulsar.bus.workflow_data_bus import workflow_data_bus
from sdk.defer_adapter.pulsar.pulsar_adapter import PulsarAdapter

from sdk.defer_adapter.run_once import run_once

_queue_adapter_var = os.environ.get('QUEUE_ADAPTER', 'pulsar')

@run_once
def collector_queue_adapter() -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':

        _adapter = Adapter(
            # TODO This is also available in collector_data_bus - could be removed
            serializers={
                "ObservationSerializer": ObservationSerializer(schema=JsonSchema(FunctionRecord)),
            },
            adapter_protocol = PulsarAdapter(collector_json_bus('event-collector-worker', 'event-collector'))
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus)
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def function_queue_adapter() -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':
        _adapter = Adapter(
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            adapter_protocol=PulsarAdapter(function_data_bus)
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus)
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def workflow_queue_adapter() -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':
        _adapter = Adapter(
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            adapter_protocol=PulsarAdapter(workflow_data_bus)
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus)
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter

@run_once
def destination_queue_adapter() -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':
        _adapter = Adapter(
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            # Add data bus
            adapter_protocol=PulsarAdapter(destination_data_bus)
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus)
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def logger_queue_adapter() -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':
        _adapter = Adapter(
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            # Add data bus
            adapter_protocol=PulsarAdapter(logger_data_bus)
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus)
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def event_property_queue_adapter() -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':

        _adapter = Adapter(
            # TODO This is also available in collector_data_bus - could be removed
            serializers={
                # "TrackerPayloadSerializer": TrackerPayloadSerializer(schema=JsonSchema(FunctionRecord)),
                "ObservationSerializer": ObservationSerializer(schema=JsonSchema(FunctionRecord)),
            },
            # adapter_protocol=PulsarAdapter(collector_data_bus('event-collector-worker','event-collector'))
            adapter_protocol=PulsarAdapter(collector_json_bus('event-property-worker','event-property'))
        )

    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus)
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter

@run_once
def ai_queue_adapter() -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':

        _adapter = Adapter(
            # TODO This is also available in collector_data_bus - could be removed
            serializers={
                "ObservationSerializer": ObservationSerializer(schema=JsonSchema(FunctionRecord)),
            },
            adapter_protocol=PulsarAdapter(collector_json_bus('ai-embedding-worker','ai-embedding-consumer'))
        )

    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus)
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter


@run_once
def ai_ner_queue_adapter() -> Adapter:
    if _queue_adapter_var.lower() == 'pulsar':
        _adapter = Adapter(
            serializers={
                "FunctionSerializer": FunctionSerializer(schema=JsonSchema(FunctionRecord)),
            },
            # Add data bus
            adapter_protocol=PulsarAdapter(ai_ner_bus)
        )
    elif _queue_adapter_var.lower() == 'kfa':
        _adapter = Adapter(
            serializers={
                "KafkaFunctionSerializer": KafkaFunctionSerializer(schema=None),
            },
            adapter_protocol=KafkaAdapter(kafka_data_bus)
        )
    elif _queue_adapter_var.lower() == 'none':
        _adapter = None
    else:
        raise ValueError(f"Unknown queue adapter `{_queue_adapter_var}`")

    return _adapter