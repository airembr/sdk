from durable_dot_dict.dotdict import DotDict


class FlatEntityHistory(DotDict):
    TS = 'ts'

    ENTITY_PK= 'entity.pk'
    ENTITY_ID = 'entity.id'
    ENTITY_IID = 'entity.iid'
    ENTITY_IID_TYPE = 'entity.iid_type'
    ENTITY_CLASSIFICATION = 'entity.classification'
    ENTITY_TYPE = 'entity.type'
    ENTITY_LABEL = 'entity.label'

    DATA_HASH = 'data_hash'
    SCHEMA_HASH = 'schema_hash'
    FIELD_HASH = 'field_hash'
    ENTITY_TRAITS = "entity.traits"
    ENTITY_TRAITS_TEXT = 'entity.traits_text'
    OBS_ID = "observation.id"
    OBSERVER_PK = "observer.pk"
    CONTEXT = "context"
    CONSENTS_GRANTED = 'consents.granted'

    REL_TYPE = 'rel.type'
    REL_LABEL = 'rel.label'

    ENTITY = 'entity'

    IS_A_ID = 'is_a.id'
    IS_A_KIND = 'is_a.kind'
    PART_OF_ID = 'part_of.id'
    PART_OF_KIND = 'part_of.kind'


    TIME_CREATE = 'time.create'
    TIME_MERGE= 'time.merge'

