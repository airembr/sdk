from typing import Generator

from airembr.sdk.storage.cache.protocol.pubsub_protocol import PubSubProtocol
from airembr.sdk.storage.cache.client.redis_client import RedisClient


class RedisPubSubAdapter(PubSubProtocol):

    def __init__(self):
        self._client = RedisClient()

    def subscribe(self, channel) -> Generator:
        subscriber = self._client.pubsub()
        subscriber.subscribe(channel)
        for message in subscriber.listen():
            yield message

    def publish(self, channel, payload):
        return self._client.publish(channel, payload)