from contextlib import contextmanager
from time import time

class Counter:
    def __init__(self):
        self.duration = 1
        self.records_total = 0
        self.records_per_message = 0
        self.messages_total = 0

    def records_per_second(self):
        return self.records_total / self.duration

@contextmanager
def time_profiler():
    t1 = time()
    counter = Counter()
    try:
        yield counter
    finally:
        counter.duration = time() - t1