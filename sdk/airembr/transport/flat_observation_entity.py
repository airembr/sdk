from typing import Optional

from durable_dot_dict.dotdict import DotDict


class ObservationEntity(DotDict):
    ENTITY = 'entity'
    ENTITY_PK = 'entity.pk'
    ENTITY_ID = 'entity.id'
    ENTITY_TYPE = 'entity.type'
    ENTITY_ROLE = 'entity.role'
    ENTITY_TRAITS = 'entity.traits'
    ENTITY_TRAITS_TEXT = 'entity.traits_text'

    DATA_HASH = 'data_hash'
    SCHEMA_HASH = 'schema_hash'
    FIELD_HASH = 'field_hash'
    OBJECT_DATA_HASH = 'object_data_hash'

    CONSENTS_GRANTED = 'consents.granted'

    TS = 'ts'

    IS_A_ID = 'is_a.id'
    IS_A_KIND = 'is_a.kind'
    PART_OF_ID = 'part_of.id'
    PART_OF_KIND = 'part_of.kind'

    TIME_CREATE = 'time.create'

    # Iternal
    _LIST_OF_PROPERTIES = 'sys_ent_property'

    @property
    def entity_id(self) -> Optional[str]:
        return self.get(self.ENTITY_ID, None)
