from durable_dot_dict.dotdict import DotDict


class FlatLogPayload(DotDict):
    ID = 'id'
    TS = 'ts'
    HEADERS = 'headers'
    OBSERVATIONS = 'observations'
