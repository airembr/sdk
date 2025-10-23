from typing import Protocol


class MessageProtocol(Protocol):

    def value(self):
        pass

    def properties(self) -> dict:
        pass

    def message(self):
        pass