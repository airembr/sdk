from contextlib import contextmanager
from time import time
from typing import Optional

from airembr.sdk.logging.log_handler import get_logger

logger = get_logger(__name__)

class Counter:
    def __init__(self):
        self.duration = 1
        self.records_total = 0
        self.records_per_message = 0
        self.messages_total = 0

    def records_per_second(self):
        return self.records_total / self.duration

@contextmanager
def time_profiler(name: Optional[str] = None):
    t1 = time()
    counter = Counter()
    try:
        yield counter
    finally:
        counter.duration = time() - t1
        if name:
            logger.info(f"{name}: {counter.duration}")