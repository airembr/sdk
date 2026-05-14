from typing import List

from airembr.model.api.request.observation import Observation
from airembr.model.metadata.sys_destination import Destination
from airembr.model.metadata.sys_resource import Resource


class TriggerInterface:

    def __init__(self, debug: bool, resource: Resource, destination: Destination):
        self.destination = destination
        self.debug = debug
        self.resource = resource

    async def dispatch(self, observations: List[Observation], job_name: str = None):
        pass

    def _get_credentials(self):
        return self.resource.credentials.test if self.debug else self.resource.credentials.production

    def __hash__(self):
        return hash(self.destination.id)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
