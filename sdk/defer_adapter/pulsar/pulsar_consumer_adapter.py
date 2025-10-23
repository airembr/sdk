from typing import Generator

import pulsar

from sdk.defer.error.client_timeout import ClientTimeOutError
from sdk.defer.protocol.queue_consumer_protocol import ConsumerProtocol
from sdk.defer.protocol.queue_message_protocol import MessageProtocol
from .pulsar_message_adapter import PulsarMessageAdapter


class PulsarConsumerAdapter(ConsumerProtocol):

    def __init__(self, consumer):
        self._consumer = consumer

    def receive(self, timeout_millis) -> Generator[PulsarMessageAdapter, None, None]:
        """
        Raises ClientTimeOutError if timeout_millis passed
        :param timeout_millis:
        :return:
        """
        while True:
            try:
                msg = self._consumer.receive(timeout_millis=timeout_millis)
                # Must be returned as PulsarMessageAdapter
                yield PulsarMessageAdapter(msg)
            except pulsar.Timeout as e:
                raise ClientTimeOutError(str(e))

    def acknowledge(self, msg: MessageProtocol):
        return self._consumer.acknowledge(msg.message())

    def negative_acknowledge(self, msg: MessageProtocol):
        return self._consumer.negative_acknowledge(msg.message())

    def identify_yourself(self):
        pass