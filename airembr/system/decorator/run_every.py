import time
from functools import wraps

def run_every(interval=60):
    """
    Decorator to ensure a function runs at most once per `interval` seconds.
    If called before the interval has passed, the previous result is returned.
    """
    def decorator(func):
        last_run = {"time": 0, "result": None}

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_run["time"] >= interval:
                last_run["time"] = now
                last_run["result"] = func(*args, **kwargs)
            return last_run["result"]

        return wrapper
    return decorator

