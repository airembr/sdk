from typing import Protocol, Generator

from sdk.defer.protocol.queue_message_protocol import MessageProtocol


class ConsumerProtocol(Protocol):

    def receive(self, timeout_millis) -> Generator[MessageProtocol, None, None]:
        """
        Raises ClientTimeOutError if timeout_millis passed
        :param timeout_millis:
        :return:
        """
        pass

    def acknowledge(self, msg: MessageProtocol):
        pass

    def negative_acknowledge(self, msg: MessageProtocol):
        pass