import time
import functools

def throttle(seconds):
    """
    Decorator to throttle a function, ensuring it runs at most once
    every `seconds`.
    """
    def decorator(func):
        last_called = 0  # simple variable now

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_called  # allows modifying the outer variable
            now = time.time()
            if now - last_called >= seconds:
                last_called = now
                return func(*args, **kwargs)
            return None
        return wrapper
    return decorator
