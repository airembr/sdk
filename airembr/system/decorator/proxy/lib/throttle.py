import time
from contextlib import contextmanager
from collections import defaultdict
from typing import Callable, Any, Awaitable

from airembr.system.decorator.proxy.lib.status import Status


@contextmanager
def timer(current_time, status: Status, cache_status, func_status, value_status):
    yield
    status.in_memory_cache = (
        cache_status,
        func_status,
        value_status
    )
    status.local_cache_time = time.time() - current_time
    if status.global_cache_time:
        status.local_cache_time -= status.global_cache_time


class Throttler:
    cached_results = defaultdict(dict)
    _last_time_func_call = {}

    def __init__(self, return_cache_when_throttled: bool = True):
        self._return_cache_when_throttled = return_cache_when_throttled
        self._last_run_time = 0

    async def _run(self, key, current_time, func, args, kwargs):
        try:
            result = await func(*args, **kwargs)
            Throttler.cached_results[key] = result
            return result
        finally:
            self._last_run_time = current_time
            Throttler._last_time_func_call[key] = current_time

    @staticmethod
    def _cached(key):
        return key in Throttler.cached_results

    @staticmethod
    def _get_last_func_run_time(key, current_time) -> float:
        return current_time - Throttler._last_time_func_call.get(key, 0)

    def _get_last_throttle_run_time(self, current_time) -> float:
        return current_time - self._last_run_time

    def _is_expired(self, cache_ttl, current_time):
        """
        Throttle means I can call function because I am allowed to.
        """
        return self._get_last_throttle_run_time(current_time) <= cache_ttl

    def _is_overdue(self, key, current_time, max_no_execution):
        """
        Overdue means I must call function because it waited too long.
        """
        return self._get_last_func_run_time(key, current_time) >= max_no_execution

    async def call(self, status: Status, cache_ttl, max_no_execution, key, func: Callable[..., Awaitable[Any]], args,
                   kwargs) -> Any:
        # Create a unique key based on function arguments

        current_time = time.time()

        # Check if the function can be executed
        if not self._cached(key):
            with timer(current_time,
                       status,
                       ('no-local-cache', 'empty'),
                       ('global-cache-fetched', 'in-memory-cache-filled'),
                       'TRY-CACHE'
                       ):
                return await self._run(key, current_time, func, args, kwargs)
        elif self._is_overdue(key, current_time, max_no_execution):
            with timer(current_time,
                       status,
                       ('no-local-cache', 'overdue'),
                       ('global-cache-fetched', 'in-memory-cache-filled'),
                       'TRY-CACHE'
                       ):
                return await self._run(key, current_time, func, args, kwargs)
        elif not self._is_expired(cache_ttl, current_time):
            with timer(current_time,
                       status,
                       ('no-local-cache', 'expired'),
                       ('global-cache-fetched', 'in-memory-cache-filled'),
                       'TRY-CACHE'
                       ):
                return await self._run(key, current_time, func, args, kwargs)

        # Throttled
        if not self._return_cache_when_throttled:
            with timer(current_time,
                       status,
                       ('local-cache', 'available'),
                       ('global-cache-NOT-fetched', 'in-memory-cache-NOT-filled'),
                       'NONE'
                       ):
                return None

        with timer(current_time,
                   status, ('local-cache', 'available'),
                   ('global-cache-NOT-fetched', 'in-memory-cache-NOT-filled'),
                   'MEMORY'
                   ):
            return Throttler.cached_results.get(key, None)
