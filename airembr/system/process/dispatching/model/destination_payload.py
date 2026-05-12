from pydantic import BaseModel

from airembr.model.metadata.sys_destination import Destination
from airembr.model.metadata.sys_resource import Resource
from airembr.system.process.dispatching.trigger_interface import TriggerInterface


class DestinationPayload(BaseModel):
    destination: Destination
    resource: Resource

    def get_destination_instance(self, debug) -> TriggerInterface:
        destination_class = self.destination.get_destination_class()
        return destination_class(debug, self.resource, self.destination)

    def __hash__(self):
        return hash(self.destination.id)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
