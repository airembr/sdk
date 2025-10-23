from typing import Optional

from pulsar.schema import Schema

from .pulsar_client import PulsarClient, PulsarTopic

_topics_producers = {}


def _create_producer(pulsar_client: PulsarClient, topic: str, schema: Optional[Schema] = None):
    _pulsar_system_topic = PulsarTopic(pulsar_client, topic)
    return _pulsar_system_topic.producer(schema=schema)


def topic_producer_factory(pulsar_client: PulsarClient, topic: str, schema: Optional[Schema] = None):
    # Cached per topic
    if topic not in _topics_producers:
        _topics_producers[topic] = _create_producer(pulsar_client, topic, schema)
    return _topics_producers[topic]
