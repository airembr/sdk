from typing import Protocol, Tuple, Any

from sdk.defer.model.transport_context import TransportContext


class SerializerProtocol(Protocol):

    def __init__(self, schema=None):
        pass

    def serialize(self, data, event_name: str, context: TransportContext) -> Tuple[Any, Any]:
        # Takes data serializes it and construct a pulsar Record
        pass

    def deserialize(self, record) -> Tuple[tuple, dict, dict]:
        # Takes object and unserialize the params and returns Function, args, kwargs, context
        pass

    def schema(self):
        pass
