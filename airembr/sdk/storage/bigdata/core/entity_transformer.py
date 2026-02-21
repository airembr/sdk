from typing import List

from durable_dot_dict.dotdict import DotDict

from airembr.sdk.common.date import now_in_utc
from airembr.sdk.storage.bigdata.flat_ent_property import FlatEntityProperty
from airembr.sdk.transport.flat_relation import FlatRelation


def _compute_properties_from_traits(relation: DotDict):
    traits = DotDict(relation[FlatRelation.ENTITY_TRAITS])
    for key, value in traits.flat().items():
        row = {
            FlatEntityProperty.PK: relation[FlatRelation.ENTITY_PK],
            FlatEntityProperty.ID: relation[FlatRelation.ENTITY_ID],
            FlatEntityProperty.TYPE: relation[FlatRelation.ENTITY_TYPE],
            FlatEntityProperty.NAME: key,
            FlatEntityProperty.VALUE: value,
        }

        if isinstance(value, (int, float)):
            row[FlatEntityProperty.NUMBER] = value
        else:
            if isinstance(value, str):
                row[FlatEntityProperty.TEXT] = value

        yield row


def compute_entity_property_from_entities(storage_context_entities: List[DotDict]):
    for entity in storage_context_entities:
        if isinstance(entity, FlatRelation):
            # For for_rel
            entity_properties = _compute_properties_from_traits(entity)
        else:
            #  for_entity(FlatEntity)
            entity_properties = _compute_properties_from_traits(entity)

        _observer_pk = entity[FlatRelation.OBSERVER_PK]
        for row in entity_properties:
            # TODO this can be an issue as TS is added late in the pipeline
            row[FlatEntityProperty.TS] = now_in_utc()
            row[FlatEntityProperty.OBSERVER_PK] = _observer_pk
            yield row