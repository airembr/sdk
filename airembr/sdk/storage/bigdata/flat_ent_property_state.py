from durable_dot_dict.dotdict import DotDict


class FlatEntityPropertyState(DotDict):
    ENTITY_PK = 'entity.pk'
    ENTITY_TYPE = 'entity.type'

    NAME = "property.name"
    VALUE = "property.value"
    TEXT = "property.text"
    NUMBER = "property.number"
    VECTOR = "property.vector"
    TS = 'ts'

    OBSERVER_PK = 'observer.pk'

