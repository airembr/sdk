import hashlib
import orjson

def dict_hash(d: dict) -> str:
    encoded = orjson.dumps(
        d,
        option=orjson.OPT_SORT_KEYS
    )
    return hashlib.sha1(encoded).hexdigest()
