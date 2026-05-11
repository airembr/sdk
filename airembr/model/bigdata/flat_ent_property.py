from durable_dot_dict.dotdict import DotDict


class FlatEntityProperty(DotDict):
    PK = 'entity.pk'
    ID = 'entity.id'
    TYPE = 'entity.type'

    PROPERTY_ID = "property.id"
    NAME = "property.name"
    VALUE = "property.value"
    TEXT = "property.text"
    NUMBER = "property.number"
    VECTOR = "property.vector"
    TS = 'ts'

    OBSERVER_PK = 'observer.pk'

    _IS_RELATION = '_is_relation'

