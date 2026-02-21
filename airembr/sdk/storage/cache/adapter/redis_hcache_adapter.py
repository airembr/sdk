from typing import List

from airembr.sdk.storage.cache.protocol.hcache_protocol import HCacheProtocol
from airembr.sdk.storage.cache.client.redis_client import RedisClient


class RedisHCacheAdapter(HCacheProtocol):
    def __init__(self):
        self._client = RedisClient()

    def hexists(self, name, key):
        return self._client.hexists(name, key)

    def hset(self, name, key, value):
        return self._client.hset(name, key, value)

    def hget(self, name, key):
        return self._client.hget(name, key)

    def hdel(self, name: str, *keys: List):
        return self._client.hdel(name, *keys)