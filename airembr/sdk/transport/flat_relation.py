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
    ENTITY_CLASSIFICATION = 'entity.classification'
    OBS_ID = "observation.id"
    CONTEXT = "context"
    CONSENTS_GRANTED = 'consents.granted'
    OBSERVER_PK = 'observer.pk'
    SESSION_ID = 'session.id'

    REL_TYPE = 'rel.type'
    REL_LABEL = 'rel.label'

    # Iternal
    _OBSERVER_ID = 'sys_ent_property_observer_id'
