from airembr.sdk.storage.bigdata.flat_ent_history import FlatEntityHistory
from airembr.sdk.transport.flat_obs_2_entity import FlatObs2Entity


def get_obs_2_entity_object(observation_id, entity, session_id: str = None):
    return {
        FlatObs2Entity.OBSERVATION_ID: observation_id,
        FlatObs2Entity.ENTITY_ID: entity[FlatEntityHistory.ENTITY_ID],
        FlatObs2Entity.ENTITY_PK: entity[FlatEntityHistory.ENTITY_PK],
        FlatObs2Entity.ENTITY_TYPE: entity[FlatEntityHistory.ENTITY_TYPE],
        FlatObs2Entity.ENTITY_DATA_HASH: entity[FlatEntityHistory.DATA_HASH],
        FlatObs2Entity.SESSION_ID: session_id
    }
