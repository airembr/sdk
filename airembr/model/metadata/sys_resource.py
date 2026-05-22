from datetime import datetime
from typing import Optional, Any, List, Union, Type, TypeVar

from pydantic import BaseModel

from airembr.model.metadata.sys_destination import DestinationConfig
from airembr.model.system.named_entity import NamedEntityInContext
from airembr.model.system.context import get_context
from airembr_sdk.core.date import now_in_utc

T = TypeVar("T")


class ResourceCredentials(BaseModel):
    production: Optional[dict] = {}
    test: Optional[dict] = {}

    def get_credentials(self, plugin, output: Type[T] = None) -> Union[T, dict]:
        """
        Returns configuration of resource depending on the state of the executed workflow: test or production.
        """

        if plugin.debug is True or not get_context().production:
            return output(**self.test) if output is not None else self.test
        return self.get_production_credentials(output)

    def get_production_credentials(self, output: Type[T] = None) -> Union[T, dict]:
        return output(**self.production) if output is not None else self.production


class Resource(NamedEntityInContext):
    type: str
    timestamp: Optional[datetime] = None
    description: Optional[str] = "No description provided"
    credentials: ResourceCredentials = ResourceCredentials()
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    icon: Optional[str] = None
    destination: Optional[DestinationConfig] = None
    enabled: Optional[bool] = True
    locked: Optional[bool] = False

    def __init__(self, **data: Any):
        data['timestamp'] = now_in_utc()
        super().__init__(**data)

    def is_destination(self):
        return self.destination is not None
