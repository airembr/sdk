from typing import Optional, List, Callable, Dict
from pydantic import field_validator, BaseModel
from airembr_sdk.api.model.entity import Entity
from airembr.model.system.named_entity import NamedEntity, NamedEntityInContext
from airembr.core.package.invoker import load_callable, import_package
from airembr.core.security.b64 import b64_decoder, b64_encoder


class DestinationConfig(BaseModel):
    package: str
    init: dict = {}
    form: dict = {}
    outbound: Optional[str] = 'resource'

    @field_validator("package")
    @classmethod
    def package_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Destination package cannot be empty")
        return value

    def encode(self):
        return b64_encoder(self)

    @staticmethod
    def decode(encoded_string) -> "DestinationConfig":
        return DestinationConfig(
            **b64_decoder(encoded_string)
        )


class DestinationTrigger(BaseModel):
    type: NamedEntity
    config: Optional[Dict] = {}

    def get_config_as_int(self, value, default=None):
        if value not in self.config:
            return default

        value = self.config[value]
        if isinstance(value, str) and not value.isdigit():
            value = default
        else:
            value = int(value)
        return value

class DestinationResource(Entity):
    type: str

class Destination(NamedEntityInContext):
    description: Optional[str] = ""
    destination: DestinationConfig
    enabled: bool = False
    tags: List[str] = []
    on_profile_change_only: Optional[bool] = True
    trigger_type: Optional[int] = 1
    resource: DestinationResource
    event_type: Optional[NamedEntity] = None
    source: NamedEntity
    locked: Optional[bool] = False
    trigger: DestinationTrigger

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Name cannot be empty")
        return value

    def _get_class_and_module(self):
        parts = self.destination.package.split(".")
        if len(parts) < 2:
            raise ValueError(f"Can not find class in package on {self.destination.package}")
        return ".".join(parts[:-1]), parts[-1]

    def get_destination_class(self) -> Callable:
        module, class_name = self._get_class_and_module()
        module = import_package(module)
        return load_callable(module, class_name)

    def is_workflow_resource(self) -> bool:
        return self.resource.type == 'workflow'
