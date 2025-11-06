from typing import Generator

from pararun.error.client_timeout import ClientTimeOutError
from pararun.protocol.queue_consumer_protocol import ConsumerProtocol
from pararun.protocol.queue_message_protocol import MessageProtocol
from pararun_adapter.kafka.kafka_message_adapter import KafkaMessageAdapter


class KafkaConsumerAdapter(ConsumerProtocol):

    def __init__(self, consumer):
        self._consumer = consumer

    def receive(self, timeout_millis) -> Generator[KafkaMessageAdapter, None, None]:
        """
        Raises ClientTimeOutError if timeout_millis passed
        :param timeout_millis:
        :return:
        """

        while True:
            # Poll for messages with a timeout
            msg_pack = self._consumer.poll(timeout_ms=timeout_millis)

            if msg_pack:
                for tp, messages in msg_pack.items():
                    for message in messages:
                        yield KafkaMessageAdapter(message)
            else:
                raise ClientTimeOutError("Kafka time-out")

        # for message in self._consumer:
        #     yield KafkaMessageAdapter(message)

    def acknowledge(self, msg: MessageProtocol):
        return self._consumer.commit()

    def negative_acknowledge(self, msg: MessageProtocol):
        return None
