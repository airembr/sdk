import time
import hashlib
import uuid


def get_time_based_uuid(interval_seconds=15*60) -> str:
    """
    Returns a UUID that changes every `interval_seconds` seconds,
    deterministic across distributed nodes.
    """
    now = int(time.time())  # current Unix time in seconds
    time_slot = now // interval_seconds  # current 2-second slot

    # Use a hash of the time slot to generate a UUID
    hash_bytes = hashlib.md5(str(time_slot).encode()).digest()
    return str(uuid.UUID(bytes=hash_bytes))
