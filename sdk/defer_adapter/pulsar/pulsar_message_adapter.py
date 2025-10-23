from sdk.defer.protocol.queue_message_protocol import MessageProtocol


class PulsarMessageAdapter(MessageProtocol):

    def __init__(self, message):
        self._message = message

    def value(self):
        return self._message.value()

    def properties(self):
        return self._message.properties()

    def message(self):
        return self._message