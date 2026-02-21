from durable_dot_dict.dotdict import DotDict


class FlatRelation(DotDict):
    TS = 'ts'
    ENTITY_PK = 'entity.pk'
    ENTITY_ID = 'entity.id'
    ENTITY_TYPE = 'entity.type'
    DATA_HASH = 'data_hash'
    SCHEMA_HASH = 'schema_hash'
    ENTITY_TRAITS = "entity.traits"
    ENTITY_TRAITS_TEXT = "entity.traits_text"
    OBS_ID = "observation.id"
    CONTEXT = "context"
    CONSENTS_GRANTED = 'consents.granted'
    OBSERVER_PK = 'observer.pk'

    # Iternal
    _OBSERVER_ID = 'sys_ent_property_observer_id'
