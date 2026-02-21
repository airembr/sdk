import msgpack
from airembr.sdk.storage.cache.protocol.cache_protocol import CacheProtocol
from airembr.sdk.storage.cache.client.redis_client import RedisClient


class RedisListCacheAdapter(CacheProtocol):

    def __init__(self, prefix: str = None):
        self.prefix = prefix
        self._client = RedisClient()

    def _full_key(self, key: str) -> str:
        # Optional: prefix keys to avoid conflicts
        if self.prefix:
            return f"{self.prefix}:{key}"
        return key

    # ----------------- List operations -----------------

    def set(self, key, value, ex=None, nx:bool=None):
        full_key = self._full_key(key)
        return self._client.set(full_key, value, ex=ex, nx=nx)

    def get(self, key: str):
        full_key = self._full_key(key)
        return self._client.get(full_key)

    def rpush(self, key: str, *value):
        """Append value to the end of the list"""
        full_key = self._full_key(key)
        return self._client.rpush(full_key, *value)

    def lpush(self, key: str, *value):
        """Push value to the start of the list"""
        full_key = self._full_key(key)
        return self._client.lpush(full_key, *value)

    def lrange(self, key: str, start: int = 0, end: int = -1):
        """Get a range of elements from the list"""
        full_key = self._full_key(key)
        return self._client.lrange(full_key, start, end)

    def lindex(self, key: str, index: int):
        """Get an element by index"""
        full_key = self._full_key(key)
        return self._client.lindex(full_key, index)

    def lset(self, key: str, index: int, value):
        """Set an element at a specific index"""
        full_key = self._full_key(key)
        return self._client.lset(full_key, index, value)

    def expire(self, key: str, ttl: int):
        """Set TTL on the list"""
        full_key = self._full_key(key)
        return self._client.expire(full_key, ttl)

    def ttl(self, key: str):
        """Set TTL on the list"""
        full_key = self._full_key(key)
        return self._client.ttl(full_key)

    def delete(self, key: str):
        """Delete the list"""
        full_key = self._full_key(key)
        return self._client.delete(full_key)

    # ----------------- Optional msgpack helpers -----------------

    def rpush_msgpack(self, key: str, value):
        packed = msgpack.packb(value, default=str)
        return self.rpush(key, packed)

    def lrange_msgpack(self, key: str, start: int = 0, end: int = -1):
        items = self.lrange(key, start, end)
        return [msgpack.unpackb(item) for item in items if item is not None]
