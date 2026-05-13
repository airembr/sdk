from typing import Dict
from uuid import uuid4

from durable_dot_dict.dotdict import DotDict

from airembr_sdk.core.entity.identification import generate_hid
from airembr.model.system.observation import Observation, ObservationEntity
from airembr.core.hash.data_hasher import hash_dict_64
from airembr.system.utils.text.formaters import _stringify_dict
from airembr_sdk.core.date import now_in_utc
from airembr.model.bigdata.flat_ent_property import FlatEntityProperty
from airembr.model.bigdata.flat_ent_2_gid import FlatEntity2Gid
from airembr.model.bigdata.flat_observation_entity import ObservationEntity as FlatObsEntity
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)


def _compute_properties_from_traits(entity: DotDict):
    traits = DotDict(entity[FlatObsEntity.ENTITY_TRAITS])
    for key, value in traits.flat().items():
        row = {
            FlatEntityProperty.PK: entity[FlatObsEntity.ENTITY_PK],
            FlatEntityProperty.ID: entity[FlatObsEntity.ENTITY_ID],
            FlatEntityProperty.TYPE: entity[FlatObsEntity.ENTITY_TYPE],
            FlatEntityProperty.NAME: key,
            FlatEntityProperty.VALUE: value,
        }

        if isinstance(value, (int, float)):
            row[FlatEntityProperty.NUMBER] = value
            row[FlatEntityProperty.TEXT] = str(value).lower()
        elif isinstance(value, list):
            row[FlatEntityProperty.TEXT] = ", ".join(value)
        else:
            if isinstance(value, str):
                row[FlatEntityProperty.TEXT] = value

        yield row


def compute_data_hashes(indexed_entities: Dict[str, DotDict]) -> Dict[str, DotDict]:
    # Caution: Mutates indexed_entities
    for _, entity in indexed_entities.items():

        # When finished, recompute data hashes as traits has changed.
        # If not done, cache will stop this entity change to be saved
        traits = entity.get(FlatObsEntity.ENTITY_TRAITS, None)

        if traits is None:
            # If no traits
            entity[FlatObsEntity.DATA_HASH] = "-1"
            entity[FlatObsEntity.SCHEMA_HASH] = "-1"
            entity[FlatObsEntity.FIELD_HASH] = None
            entity[FlatObsEntity.ENTITY_TRAITS_TEXT] = ""

        else:

            entity[FlatObsEntity.DATA_HASH] = hash_dict_64(traits, dump_schema=True)
            fields = sorted(DotDict(traits).flat())
            entity[FlatObsEntity.SCHEMA_HASH] = hash_dict_64(fields)
            entity[FlatObsEntity.FIELD_HASH] = [hash_dict_64(field, dump_schema=False) for field in
                                                fields] if fields else None
            entity[FlatObsEntity.ENTITY_TRAITS_TEXT] = _stringify_dict(traits)

        # Now we can add History ID:
        entity[FlatObsEntity.ENTITY_HID] = generate_hid(entity[FlatObsEntity.ENTITY_PK],
                                                        entity[FlatObsEntity.DATA_HASH])

    return indexed_entities


def link_state_entities(indexed_entities: Dict[str, DotDict]) -> Dict[str, DotDict]:
    # Caution: Mutates indexed_entities
    for entity_id, entity in indexed_entities.items():
        if FlatObsEntity.ENTITY_STATE in entity:
            for state_trait_key, state_ref in entity[FlatObsEntity.ENTITY_STATE].items():
                if state_ref in indexed_entities:
                    state = indexed_entities.get(state_ref, None)
                    state_id = state.get(FlatObsEntity.ENTITY_ID, None)
                    if state is None or state_id is None:
                        continue
                    state_traits = state.get(FlatObsEntity.ENTITY_TRAITS, None)

                    if state_traits is None:
                        continue

                    if FlatObsEntity.ENTITY_TRAITS_STATE not in entity:
                        entity[FlatObsEntity.ENTITY_TRAITS_STATE] = {}

                    state_data = {
                        **state_traits,
                        "_id": state_id
                    }
                    entity[FlatObsEntity.ENTITY_TRAITS_STATE][state_trait_key] = state_data

    return indexed_entities


def get_entity_gids(entities_by_ref):
    return [
        {
            FlatEntity2Gid.TS: now_in_utc(),
            FlatEntity2Gid.ENTITY_GID_TYPE: item[FlatObsEntity.ENTITY_IID_TYPE],
            FlatEntity2Gid.ENTITY_TYPE: item[FlatObsEntity.ENTITY_TYPE],
            FlatEntity2Gid.ENTITY_PK: item[FlatObsEntity.ENTITY_PK],
            FlatEntity2Gid.ENTITY_GID: item[FlatObsEntity.ENTITY_IID]
        }
        for item in entities_by_ref.values()
        if item.get_or_none(FlatObsEntity.ENTITY_IID)
    ]


def index_entities(observation: Observation) -> Dict[str, DotDict]:
    # Get Entities
    observer = observation.get_observer()
    _entities_by_ref = {}
    for link, observed_entity in observation.entities.root.items():  # type: ObservationEntity

        instance = observed_entity.instance
        traits = observed_entity.traits
        state = observed_entity.state

        try:
            entity_id = instance.resolve_id(properties=traits, generate_id=True)
        except ValueError as e:
            logger.warning(
                f"Could not compute entity id for reference: '{link}'. Random id generated. Detail: {str(e)}")
            entity_id = str(uuid4())
        now = str(now_in_utc())
        flat_obs_ent = FlatObsEntity() << {
            FlatObsEntity.OBS_ID: observation.id,
            # Primary key for entity, primary key for entity is globally identifiable ID as it consist of entity type and ID
            FlatObsEntity.ENTITY_PK: instance.generate_pk(entity_id),
            # IID is identification ID if entity can be identified by defined traits
            FlatObsEntity.ENTITY_IID: observed_entity.iid.iid,
            # IID type
            FlatObsEntity.ENTITY_IID_TYPE: observed_entity.iid.type,
            # Entity ID
            FlatObsEntity.ENTITY_ID: entity_id,
            FlatObsEntity.ENTITY_TYPE: instance.kind,
            FlatObsEntity.ENTITY_ROLE: instance.role,
            FlatObsEntity.ENTITY_LABEL: observed_entity.label,
            FlatObsEntity.TS: now,
            FlatObsEntity.TIME_CREATE: now,
            FlatObsEntity.CONSENTS_GRANTED: observation.get_consents(),
            FlatObsEntity._OBSERVER_ID: observer.instance.id,
            FlatObsEntity.OBSERVER_PK: observer.instance.generate_pk(),
            FlatObsEntity.ENTITY_CLASSIFICATION: 'entity',
            FlatObsEntity.SESSION_ID: observation.session.id,
        }

        if observed_entity.is_a:
            flat_obs_ent[FlatObsEntity.IS_A_ID] = observed_entity.is_a.id
            flat_obs_ent[FlatObsEntity.IS_A_KIND] = observed_entity.is_a.kind
        else:
            flat_obs_ent[FlatObsEntity.IS_A_ID] = None
            flat_obs_ent[FlatObsEntity.IS_A_KIND] = None

        if observed_entity.part_of:
            flat_obs_ent[FlatObsEntity.PART_OF_ID] = observed_entity.part_of.id
            flat_obs_ent[FlatObsEntity.PART_OF_KIND] = observed_entity.part_of.kind
        else:
            flat_obs_ent[FlatObsEntity.PART_OF_ID] = None
            flat_obs_ent[FlatObsEntity.PART_OF_KIND] = None

        if traits:
            flat_obs_ent[FlatObsEntity.ENTITY_TRAITS] = traits
        else:
            flat_obs_ent[FlatObsEntity.ENTITY_TRAITS] = {}

        if state:
            flat_obs_ent[FlatObsEntity.ENTITY_STATE] = state

        _entities_by_ref[link] = flat_obs_ent

    return _entities_by_ref
