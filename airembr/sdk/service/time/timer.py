from contextlib import contextmanager
from time import time

class Counter:
    def __init__(self):
        self.elapsed = 1
        self.records_total = 0
        self.records_per_message = 0
        self.messages_total = 0

    def records_per_second(self):
        return self.records_total / self.elapsed

@contextmanager
def timer():
    t1 = time()
    counter = Counter()
    try:
        yield counter
    finally:
        counter.elapsed = time() - t1