from datetime import datetime

import json

from typing import Optional, TypeVar, Type, List, Union, Tuple
from uuid import uuid4
from pydantic import BaseModel

from sdk.airembr.model.time import Time, EventTime
from durable_dot_dict.dotdict import DotDict


T = TypeVar("T")


class Creatable(BaseModel):

    @classmethod
    def create(cls: Type[T], record) -> Optional[T]:
        if not record:
            return None

        obj = cls(**dict(record))

        if hasattr(obj, 'set_meta_data'):
            obj.set_meta_data(record.get_meta_data())
        return obj


class NullableEntity(Creatable):
    id: Optional[str] = None


class NullablePrimaryEntity(NullableEntity):
    primary_id: Optional[str] = None


class Entity(Creatable):
    id: str

    @staticmethod
    def new() -> 'Entity':
        return Entity(id=str(uuid4()))

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id if isinstance(other, Entity) else False


class DefaultEntity(Entity):
    metadata: Optional[Time] = None

    def get_times(self) -> Tuple[Optional[datetime], Optional[datetime], Optional[datetime]]:
        return self.metadata.insert, self.metadata.update, self.metadata.create


class PrimaryEntity(Entity):
    primary_id: Optional[str] = None
    metadata: Optional[Time] = None
    ids: Optional[List[str]] = None


class DotDictEncoder(json.JSONEncoder):
    """Helper class for encoding of nested DotDict dicts into standard dict
    """

    def default(self, obj):
        """Return dict data of DotDict when possible or encode with standard format

        :param object: Input object
        :return: Serializable data
        """
        try:
            if isinstance(obj, datetime):
                # Convert datetime to an ISO formatted string
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return json.JSONEncoder.default(self, obj)
        except TypeError:
            return str(obj)


class FlatEntity(DotDict):

    ID = "hash"  # Primary Key for Entity
    HASH = 'hash'
    TIME = "time"
    METADATA = "metadata"
    METADATA_TIME = "metadata.time"
    METADATA_TIME_INSERT = "metadata.time.insert"
    METADATA_TIME_CREATE = "metadata.time.create"
    METADATA_TIME_UPDATE = "metadata.time.update"

    def __init__(self, dictionary):
        super().__init__(dictionary)
        self._metadata = None

    def __getstate__(self):
        # Here, you should retrieve the state, not set it.
        state = {
            '_data':super().__getstate__(),
            '_metadata':  self._metadata,
        }
        return state

    def __setstate__(self, state):
        # Here, you should call the base class' setstate, not getstate.
        super().__setstate__(state.get('_data', {}))
        self._metadata = state.get('_metadata', None)

    def override(self, key, value):
        # This one does not record changes or checks for PCP
        super().__setitem__(key, value)

    def has_changes(self) -> bool:
        return bool(self._changes) and self._changes.has_changes()


    def to_json(self, default=None, cls=None):
        """Return wrapped dictionary as json string.
        This method does not copy wrapped dictionary.
        :return str: Wrapped dictionary as json string
        """
        return super().to_json(cls=DotDictEncoder)

    def instanceof(self, field: str, instance: Union[type, tuple]) -> bool:
        if field not in self:
            return False
        return isinstance(self.get(field, None), instance)

    @property
    def id(self) -> Optional[str]:
        return self.get(FlatEntity.ID, None)

    @id.setter
    def id(self, value: str):
        """Setter method"""
        if not isinstance(value, str):
            raise ValueError("ID value must be a string.")

        self[FlatEntity.ID] = value

    @property
    def hash(self) -> Optional[str]:
        return self.get(FlatEntity.HASH, None)

    @property
    def metadata_time(self) -> Optional[EventTime]:
        return EventTime(**self.get(FlatEntity.METADATA_TIME, {}))

