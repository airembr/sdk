from airembr.model.bigdata.flat_ent import FlatEntity

class FlatSysTimer(FlatEntity):
    ID = "id"

    SOURCE_ID = 'source.id'
    STATUS = 'status'
    TS = 'ts'
    TIMEOUT = 'timeout'
    EVENT = 'event'

    ACTOR_ID = 'actor.id'
    ACTOR_TYPE = 'actor.type'
    ACTOR_ROLE = 'actor.role'
    ACTOR_DATA_HASH = 'actor.data_hash'

    OBJECT_ID = 'object.id'
    OBJECT_TYPE = 'object.type'
    OBJECT_ROLE = 'object.role'
    OBJECT_DATA_HASH = 'object.data_hash'

    OBS_ID = 'obs.id'
    OBS_LABEL = 'obs.label'

    TRAITS = 'properties'

