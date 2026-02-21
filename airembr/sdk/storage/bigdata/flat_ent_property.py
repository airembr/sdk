from durable_dot_dict.dotdict import DotDict


class FlatEntityProperty(DotDict):
    PK = 'entity.pk'
    ID = 'entity.id'
    TYPE = 'entity.type'

    NAME = "property.name"
    VALUE = "property.value"
    TEXT = "property.text"
    NUMBER = "property.number"
    TS = 'ts'

    OBSERVER_PK = 'observer.pk'
