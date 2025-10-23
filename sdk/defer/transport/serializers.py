import io

import base64
import json
import pickle
from sdk.defer.transport.unpickler import DebugUnpickler


class PickleSerializer:

    @staticmethod
    def serialize(obj):
        message_bytes = pickle.dumps(obj)
        base64_bytes = base64.b64encode(message_bytes)
        txt = base64_bytes.decode('ascii')
        return txt

    @staticmethod
    def deserialize(txt):
        base64_bytes = txt.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        obj = pickle.loads(message_bytes)
        return obj

    @staticmethod
    def debug_deserialize(txt):
        # Used only when debugging deserialization
        base64_bytes = txt.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        bytes_stream = io.BytesIO(message_bytes)
        debug = DebugUnpickler(bytes_stream)
        obj = debug.load()
        return obj


class BinaryPickleSerializer:

    @staticmethod
    def serialize(obj):
        return pickle.dumps(obj)

    @staticmethod
    def deserialize(message_bytes):
        return pickle.loads(message_bytes)


class JsonSerializer:

    @staticmethod
    def serialize(obj):
        return json.dumps(obj, default=str)

    @staticmethod
    def deserialize(message):
        return json.loads(message)
