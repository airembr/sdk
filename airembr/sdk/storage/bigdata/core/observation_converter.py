from airembr.sdk.transport.flat_obs_2_entity import FlatObs2Entity
from airembr.sdk.transport.flat_relation import FlatRelation


def get_obs_2_entity_object(observation_id, entity):
    return {
        FlatObs2Entity.OBSERVATION_ID: observation_id,
        FlatObs2Entity.ENTITY_ID: entity[FlatRelation.ENTITY_ID],
        FlatObs2Entity.ENTITY_TYPE: entity[FlatRelation.ENTITY_TYPE],
        FlatObs2Entity.ENTITY_DATA_HASH: entity[FlatRelation.DATA_HASH],
    }