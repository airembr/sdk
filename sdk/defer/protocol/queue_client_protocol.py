from typing import Protocol, Optional, Any, Callable

from sdk.defer.model.data_bus import DataBus
from sdk.defer.protocol.queue_consumer_protocol import ConsumerProtocol


class QueueProtocol(Protocol):

    def publish(self, payload, on_error: Callable) -> Optional[Any]:  # Should return ID if None means error
        """
        Must serialize and publish data. Should return ID if None means error
        """

        pass

    def consumer(self) -> ConsumerProtocol:
        """
        Must read and deserialize data
        :return:
        """
        pass

    def data_bus(self)->DataBus:
        pass
