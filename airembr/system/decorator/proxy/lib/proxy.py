import pickle
from random import randint

from time import time
from typing import Optional, List, Awaitable, Any, Callable

from airembr.system.logging.log_handler import get_logger
from airembr.system.decorator.proxy.lib.status import Status
from airembr.system.decorator.proxy.lib.throttle import Throttler
from airembr.system.decorator.proxy.lib.locker import distributed_lock

from airembr.system.adapter.cache.cache_adaper_selector import cache_adapter

_cache = cache_adapter()
_week = 60 * 60 * 24 * 7
logger = get_logger(__name__)


def delete_keys_with_prefix(prefix: str):
    # Use scan_iter to find keys with the specified prefix
    pattern = f"{prefix}:*"
    keys_to_delete = list(_cache.scan(pattern))
    if keys_to_delete:
        _cache.delete(keys_to_delete, skip_tenant=True)  # Bulk delete keys


class CacheProxy:
    def __init__(self, namespace: str, lock_expires: int = 60):
        self.lock_expires = lock_expires
        self.namespace = namespace

    def _namespace(self, key: str, suffix: str = None) -> str:
        if suffix:
            return f"{self.namespace}:{suffix}:{key}"
        return f"{self.namespace}:db:{key}"

    @staticmethod
    def _serialize(value) -> Optional[bytes]:
        return pickle.dumps(value)

    @staticmethod
    def _deserialize(value):
        if value is None:
            return None
        return pickle.loads(value)

    @staticmethod
    def delete_keys(prefix: str):
        # Use scan_iter to find keys with the specified prefix
        pattern = f"{prefix}:*"
        # pattern = f"*"
        keys_to_delete = list(_cache.scan(pattern))
        if keys_to_delete:
            _cache.delete(keys_to_delete, skip_tenant=True)  # Bulk delete keys

    async def invalidate(self, names: List[str],
                         func: Callable[..., Awaitable[Any]],
                         args: tuple,
                         kwargs: dict):
        result = await func(*args, **kwargs)
        for name in names:
            self.delete_keys(prefix=self._namespace(name))
        return result

    def _delete(self, key, suffix: str = None):
        _cache.delete(self._namespace(key, suffix))

    def _exists(self, key, suffix) -> bool:
        return _cache.exists(self._namespace(key, suffix))

    def _get(self, key: str, suffix: str = None):
        value = _cache.get(self._namespace(key, suffix))
        return self._deserialize(value)

    def _set(self, key, value, suffix=None, ttl=None):
        if ttl != 0:
            value = self._serialize(value)
            _cache.set(self._namespace(key, suffix), value, ex=ttl)

    async def _load_and_update(self,
                               key,
                               global_cache_ttl: int,
                               status: Status,
                               # Function to call
                               func: Callable[..., Awaitable[Any]],
                               args: tuple,
                               kwargs: dict
                               ) -> tuple:

        current_time = time()

        # Get cached data
        cached_data_exists = self._exists(key, 'db')

        # Cache exists
        if cached_data_exists > 0:
            status.cache = (
                ("global-cache", "available"),
                ("executed | NO  | UNLOCKED", "global-cache-not-filled"),
                ("CACHE")
            )
            status.global_cache_time = time() - current_time
            # Data exists, return it immediately from global cache
            return self._get(key, 'db')

        with distributed_lock(_cache, self._namespace(key), expires=self.lock_expires) as locked:
            if locked:
                fresh_data = await func(*args, **kwargs)
                self._set(key, fresh_data, ttl=global_cache_ttl)  # Update global cache
                self._set(key, fresh_data, ttl=_week, suffix='last')  # Update global cache
                status.cache = (
                    ("no-global-cache", "expired"),
                    ("executed | YES | UNLOCKED", "global-cache-filled"),
                    ('DB'))
                status.global_cache_time = time() - current_time
                return fresh_data
            else:
                # Return from global
                result = self._get(key, suffix='last')
                status.cache = (
                    ("no-global-cache", "expired"),
                    ("executed | NO  | LOCKED  ", "global-cache-not-filled"),
                    ("CACHE")
                )
                status.global_cache_time = time() - current_time
                return result

    @staticmethod
    def key(name: str,
            func: Callable[..., Awaitable[Any]],
            args: tuple,
            kwargs: dict):

        _func_key = (f"{func.__name__}", *args, frozenset(kwargs.items()))

        return f"{name}:{_func_key}"

    async def get(self,
                  name: str,
                  in_memory_cache_ttl: int,
                  global_cache_ttl: int,
                  max_no_exec_time: float,
                  cache_key_func: Optional[Callable[[tuple, dict], str]],
                  # Function to call
                  func: Callable[..., Awaitable[Any]],
                  args: tuple,
                  kwargs: dict,
                  # Local in-memory-cache
                  throttler: Throttler) -> tuple:
        t = time()

        # Get cache key
        if cache_key_func:
            key = f"{name}:{(func.__name__, cache_key_func(args, kwargs))}"
        else:
            key = self.key(name, func, args, kwargs)

        status = Status(key)

        in_memory_cache_ttl += randint(0, 15)

        try:
            # Use throttler to protect global cache
            result = await throttler.call(
                status,
                in_memory_cache_ttl,  # min cache_ttl
                max_no_exec_time,  # max_cache_ttl
                key,
                # Function to load
                self._load_and_update,
                args=(key, global_cache_ttl, status),
                kwargs={
                    "func": func,
                    "args": args,
                    "kwargs": kwargs
                }
            )
            return result, status

        except Exception as e:

            if not self._exists(key, suffix="last"):
                raise e

            logger.error(str(e))
            status.cache = (
                ('cache', 'available'),
                ("failed    | NO | UNLOCKED", "global-cache-not-filled"),
                ('CACHE')
            )

            # Return last if error when running cache update

            result = self._get(key, suffix='last')
            status.local_cache_time = time() - t
            return result, status
