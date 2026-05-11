from durable_dot_dict.dotdict import DotDict


class FlatEntityState(DotDict):
    PK = 'entity.pk'
    TYPE = 'entity.type'
    TRAITS = "entity.traits"
    TS = 'ts'
    STITCH_TS = 'stitch_ts'
