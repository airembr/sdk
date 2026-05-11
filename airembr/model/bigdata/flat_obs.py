from durable_dot_dict.dotdict import DotDict


class FlatObs(DotDict):
    ID = "id"
    SESSION_ID = "session.id"
    SOURCE_ID = "source.id"
    LABEL = "label"
    DESCRIPTION = "description"
    ENTITIES = "entities"
    TS = "ts"
    METADATA_TIME_CREATE = "metadata.time.create"
    METADATA_TIME_INSERT = "metadata.time.insert"
