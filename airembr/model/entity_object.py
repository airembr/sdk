import hashlib
from typing import Optional, List, Any, Set
from pydantic import ConfigDict, BaseModel

from durable_dot_dict.dotdict import DotDict

from airembr.core.hash.data_hasher import hash_dict_64
from airembr.model.system.named_entity import NamedEntityInContext


class EntityProperty(NamedEntityInContext):
    entity_type: str
    content_type: Optional[str] = None
    value_type: str = 'string'
    operation: Optional[str] = 'last'
    default_value: Optional[str] = None

    column: Optional[str] = None
    json_part: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    def remove_column(self):
        self.column = None
        return self


class EntityPropertyStitch(BaseModel):
    entity_type: str
    entity_property: str
    operation: Optional[str] = 'last'
    event_type: str
    event_trait: str
    enabled: Optional[bool] = True

    production: Optional[bool] = False
    running: Optional[bool] = False

    @property
    def id(self):
        return hashlib.md5(
            f"{self.entity_type}.{self.entity_property}:{self.event_type}.{self.event_trait}".encode()).hexdigest()


class EntityPropertyPayload(BaseModel):
    id: Optional[int] = None
    name: str

    content_type: Optional[str] = None
    value_type: str = 'string'
    operation: str
    default_value: Optional[str] = None

    column: Optional[str] = None
    json_part: Optional[str] = None
    table: Optional[str] = None

    production: Optional[bool] = False

    def remove_column(self):
        self.column = None
        return self


class EntityPropertyStitchPayload(BaseModel):
    entity_type: str
    entity_property: str
    event_type: str
    event_trait: str

    @property
    def id(self):
        return hashlib.md5(
            f"{self.entity_type}.{self.entity_property}:{self.event_type}.{self.event_trait}".encode()).hexdigest()

    def to_stitch(self):
        return EntityPropertyStitch(
            **self.model_dump(),
            enabled=True
        )


class EntityObjectPayload(BaseModel):
    description: Optional[str] = ""
    lock: Optional[bool] = False
    enabled: bool = True

    table: Optional[str] = None

    type: str
    pk_id: Optional[str] = None

    requires_consent: Optional[bool] = False
    consents: Optional[str] = None

    requires_merging: Optional[bool] = False
    mg_id: Optional[str] = None

    properties: Optional[List[EntityPropertyPayload]] = []
    stitches: Optional[List[EntityPropertyStitchPayload]] = []

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self._properties = {}


class EntityObject(BaseModel):
    id: str
    description: Optional[str] = ""
    label: Optional[str] = ""
    table: Optional[str] = None
    type: str
    pk_id: Optional[str] = None
    mg_id: Optional[str] = None
    consents: Optional[str] = None
    properties: Optional[List[EntityProperty]] = []
    stitches: Optional[List[EntityPropertyStitch]] = None
    requires_consent: Optional[bool] = False
    requires_merging: Optional[bool] = False
    lock: bool
    enabled: bool = True
    hash: Optional[str] = None

    production: Optional[bool] = False
    running: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self._properties = {}
        self.hash = self.hash_data()

    def hash_data(self):
        model = DotDict(self.model_dump(exclude={"hash": ..., "description": ..., "label": ..., "lock": ...})).flat()
        return hash_dict_64(model)

    def desc(self):
        return f"Schema of a {self.type} data."

    def remove_property_columns(self):
        self.table = None
        self.properties = [prop.remove_column() for prop in self.properties]

    def get_property(self, name: str) -> Optional[EntityPropertyPayload]:
        if not self._properties:
            self._properties = {item.name: item for item in self.properties}

        return self._properties.get(name, None)

    def get_stitching(self):
        for stitch in self.stitches:
            consents = None
            if self.requires_consent:
                if self.consents and self.consents.strip() != '':
                    consents = self.consents

            yield stitch.event_type, stitch.event_trait, stitch.operation, stitch.entity_type, stitch.entity_property, consents

    def _get_column_data(self):
        for item in self.properties:
            if item.column:
                column = item.column.strip()
                if column:
                    yield item.name, column

    def get_entity_2_table_mapping(self):
        return {"table": self.table, "columns": {property: column for property, column in self._get_column_data()}}

    def get_consents(self) -> Optional[Set[str]]:
        if self.requires_consent and self.consents.strip() != '':
            return set(self.consents.split(','))
        return None
