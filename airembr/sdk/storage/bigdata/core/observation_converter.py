from airembr.sdk.storage.bigdata.flat_ent_history import FlatEntityHistory
from airembr.sdk.transport.flat_obs_2_entity import FlatObs2Entity
from airembr.sdk.transport.flat_relation import FlatRelation


def get_obs_2_entity_object(observation_id, entity, session_id: str = None):
    return {
        FlatObs2Entity.OBSERVATION_ID: observation_id,
        FlatObs2Entity.ENTITY_ID: entity[FlatEntityHistory.ENTITY_ID],
        FlatObs2Entity.ENTITY_PK: entity[FlatEntityHistory.ENTITY_PK],
        FlatObs2Entity.ENTITY_TYPE: entity[FlatEntityHistory.ENTITY_TYPE],
        FlatObs2Entity.ENTITY_DATA_HASH: entity[FlatEntityHistory.DATA_HASH],
        FlatObs2Entity.SESSION_ID: session_id
    }


def get_rel_2_entity_object(observation_id, relation: FlatRelation, session_id: str = None):
    return {
        FlatObs2Entity.OBSERVATION_ID: observation_id,
        FlatObs2Entity.ENTITY_ID: relation[FlatRelation.ENTITY_ID],
        FlatObs2Entity.ENTITY_PK: relation[FlatRelation.ENTITY_PK],
        FlatObs2Entity.ENTITY_TYPE: relation[FlatRelation.ENTITY_TYPE],
        FlatObs2Entity.ENTITY_DATA_HASH: relation[FlatRelation.DATA_HASH],
        FlatObs2Entity.SESSION_ID: session_id
    }