import json

from datetime import datetime

from typing import Optional, Union
from durable_dot_dict.dotdict import DotDict


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
            '_data': super().__getstate__(),
            '_metadata': self._metadata,
        }
        return state

    def __setstate__(self, state):
        # Here, you should call the base class' setstate, not getstate.
        super().__setstate__(state.get('_data', {}))
        self._metadata = state.get('_metadata', None)

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
