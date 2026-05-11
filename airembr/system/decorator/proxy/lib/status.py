from airembr.sdk.common.date import now_in_utc
from airembr.sdk.logging.log_handler import get_logger

logger = get_logger(__name__)

def _pretty_ts():
    now = now_in_utc()
    return now.strftime("%M:%S") + f":{now.microsecond // 1000:06}"

class Status:

    def __init__(self, name):
        self.cache = None
        self.in_memory_cache = None
        self.key = name
        self.global_cache_time = 0
        self.local_cache_time = 0

    def print_in_memory(self, result, all=True):
        if self.in_memory_cache is not None:
            cache_status, function, value = self.in_memory_cache
            if all or cache_status[0] != 'local-cache':
                logger.debug(
                    f"{_pretty_ts()} | {value.ljust(10)} | {cache_status[0]}({cache_status[1]}) | {function[0]} | {self.key} |  ({self.local_cache_time:.5f})-{self.global_cache_time:.5f} | {result}")


    def print_global(self, result, all=True):
        if self.cache is not None:
            cache_status, function, value = self.cache
            if all or cache_status[0] != 'global-cache':
                logger.debug(
                        f"{_pretty_ts()} | {value.ljust(10)} | {cache_status[0]}({cache_status[1]}) | {function[0]} | {self.key} | {self.local_cache_time:.5f}-({self.global_cache_time:.5f})  | {result}")

    def __str__(self):
        return f"Status(in-memory-cache={self.in_memory_cache}, global-cache={self.cache}, key={self.key}, global_cache_time={self.global_cache_time}, , local_cache_time={self.local_cache_time})"
