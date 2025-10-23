from .pulsar_client import PulsarClient, PulsarTopic

_topics_producers = {}


def _create_subscriber(pulsar_client: PulsarClient,
                       topic: str,
                       kwargs):
    _pulsar_topic = PulsarTopic(pulsar_client, topic)
    return _pulsar_topic.subscribe(
        **kwargs
    )


def topic_subscriber_factory(
        pulsar_client: PulsarClient,
        topic: str,
        **kwargs
):
    if topic not in _topics_producers:
        _topics_producers[topic] = _create_subscriber(
            pulsar_client,
            topic,
            kwargs)
    return _topics_producers[topic]
