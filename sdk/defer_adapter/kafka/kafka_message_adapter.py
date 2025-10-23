from sdk.defer.protocol.queue_message_protocol import MessageProtocol


class KafkaMessageAdapter(MessageProtocol):

    def __init__(self, message):
        self._message = message

    def value(self):
        return self._message.value

    def properties(self) -> dict:
        # Kafka headers are [('function.name', b'my_fnc'), ('function.module', b'test.test_job'), ...]
        return {key: value.decode('utf-8') for key, value in self._message.headers}

    def message(self):
        return self._message