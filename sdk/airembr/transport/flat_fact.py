from durable_dot_dict.dotdict import DotDict


class FlatFact(DotDict):
    ID = "id"

    SESSION = 'session'
    SESSION_ID = 'session.id'

    ASPECT = 'aspect'

    SOURCE = 'source'
    SOURCE_ID = 'source.id'

    METADATA = "metadata"
    METADATA_TIME = "metadata.time"
    METADATA_TIME_INSERT = "metadata.time.insert"
    METADATA_TIME_CREATE = "metadata.time.create"
    METADATA_TIME_UPDATE = "metadata.time.update"
    METADATA_ERROR = 'metadata.error'
    METADATA_WARNING = 'metadata.warning'
    METADATA_VALID = 'metadata.valid'
    METADATA_CONTEXT_COUNT = 'metadata.context.count'
    METADATA_CONTEXT_ENTITIES = 'metadata.context.entities'

    CONSENTS_GRANTED = 'consents.granted'

    ACTOR_ID = 'actor.id'
    ACTOR_PK = 'actor.pk'  # actor.type + actor.id
    ACTOR_TYPE = 'actor.type'
    ACTOR_ROLE = 'actor.role'
    ACTOR_DATA_HASH = 'actor.data_hash'
    ACTOR_SCHEMA_HASH = 'actor.schema_hash'
    ACTOR_IS_A_ID = 'actor.is_a.id'
    ACTOR_IS_A_KIND = 'actor.is_a.kind'
    ACTOR_PART_OF_ID = 'actor.part_of.id'
    ACTOR_PART_OF_KIND = 'actor.part_of.kind'

    OBJECT_ID = 'object.id'
    OBJECT_PK = 'object.pk'  # object.type + object.id
    OBJECT_TYPE = 'object.type'
    OBJECT_ROLE = 'object.role'
    OBJECT_DATA_HASH = 'object.data_hash'
    OBJECT_SCHEMA_HASH = 'object.schema_hash'
    OBJECT_IS_A_ID = 'object.is_a.id'
    OBJECT_IS_A_KIND = 'object.is_a.kind'
    OBJECT_PART_OF_ID = 'object.part_of.id'
    OBJECT_PART_OF_KIND = 'object.part_of.kind'

    REL_ID = 'rel.id'
    REL_LABEL = 'rel.label'  # eg. viewed
    REL_TYPE = 'rel.type'  # eg. event, intent
    REL_DATA_HASH = 'rel.data_hash'
    REL_SCHEMA_HASH = 'rel.schema_hash'

    OBS_ID = 'observation.id'
    OBS_NAME = 'observation.name'

    LABEL = 'label'
    TYPE = 'type'
    CONTEXT = 'context'
    TRAITS = 'traits'
    TAGS = 'tags'

    SYS_TIMER_ID = 'sys.timer.id'
    SYS_TIMER_STATUS = 'sys.timer.status'

    DEVICE = 'device'
    DEVICE_ID = f'{DEVICE}.id'
    DEVICE_TYPE_ID = f'{DEVICE}.type_id'

    LOCATION_ID = f'location.id'

    APPLICATION_TYPE_ID = 'app.type_id'

    OS_TYPE_ID = 'os.type_id'

    HIT = 'hit.origin'

    SEMANTIC_DESCRIPTION = 'semantic.description'
    SEMANTIC_CONTEXT = 'semantic.context'
    SEMANTIC_SUMMARY = 'semantic.summary'

