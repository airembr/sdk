import contextlib
from datetime import datetime, timedelta

from airembr.core.singleton import Singleton


class TimedFlag:
    def __init__(self):
        self._value = False
        self._expiry_time = None

    def set_false(self):
        self._value = False

    def set_true(self, ttl_seconds):
        """
        Set the value to True and define the time-to-live (TTL) in seconds.
        """
        self._value = True
        self._expiry_time = datetime.now() + timedelta(seconds=ttl_seconds)

    def get_value(self):
        """
        Return the current value of the flag. If the TTL has expired, reset to False.
        """
        if self._value and self._expiry_time <= datetime.now():
            self._value = False
            self._expiry_time = None
        return self._value

    def timeout(self):
        return self._expiry_time - datetime.now()


class TimedFlags(metaclass=Singleton):
    def __init__(self):
        self._data = {}

    def set(self, key, value, ttl):
        """
        Set a timed flag for the given key with the specified TTL.
        """
        if not isinstance(value, bool):
            raise ValueError("Flag can only be bool.")

        # Retrieve existing or create a new TimedFlag
        flag: TimedFlag = self._data.get(key, TimedFlag())
        if value:
            flag.set_true(ttl)
        else:
            flag.set_false()

        # Store back the modified flag
        self._data[key] = flag

    def get(self, key) -> bool:
        """
        Get the value of the timed flag for the given key.
        """
        if key not in self._data:
            self._data[key] = TimedFlag()
        flag = self._data.get(key)
        return flag.get_value()

    def get_flag(self, key) -> TimedFlag:
        """
        Get the value of the timed flag for the given key.
        """
        if key not in self._data:
            return TimedFlag()
        return self._data.get(key)


flags = TimedFlags()


@contextlib.contextmanager
def suppress_for(key, ttl):
    if flags.get(key):
        # Suppress the body by yielding from an empty context
        yield True
    else:
        try:
            yield False
        finally:
            flags.set(key, True, ttl=ttl)
