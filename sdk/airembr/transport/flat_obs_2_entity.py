from durable_dot_dict.dotdict import DotDict


class FlatObs2Entity(DotDict):
    TS = 'ts'
    OBSERVATION_ID = 'observation.id'
    ENTITY_ID = 'entity.id'
    ENTITY_TYPE = 'entity.type'
    ENTITY_DATA_HASH = 'entity.data_hash'
