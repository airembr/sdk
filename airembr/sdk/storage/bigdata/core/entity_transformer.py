from typing import List

from durable_dot_dict.dotdict import DotDict

from airembr.sdk.common.date import now_in_utc
from airembr.sdk.service.hashes.hash import md5
from airembr.sdk.storage.bigdata.flat_ent_property import FlatEntityProperty
from airembr.sdk.transport.flat_relation import FlatRelation
from airembr.sdk.transport.flat_observation_entity import ObservationEntity


def _compute_properties_from_traits(relation: DotDict, is_relation: bool):
    traits = DotDict(relation[FlatRelation.ENTITY_TRAITS])
    for key, value in traits.flat().items():
        row = {
            FlatEntityProperty.PK: relation[FlatRelation.ENTITY_PK],
            FlatEntityProperty.ID: relation[FlatRelation.ENTITY_ID],
            FlatEntityProperty.TYPE: relation[FlatRelation.ENTITY_TYPE],
            FlatEntityProperty.NAME: key,
            FlatEntityProperty.VALUE: value,
            FlatEntityProperty._IS_RELATION: is_relation # This is not saved used only fo filtering
        }

        if isinstance(value, (int, float)):
            row[FlatEntityProperty.NUMBER] = value
        else:
            if isinstance(value, str):
                row[FlatEntityProperty.TEXT] = value

        yield row


def compute_entity_property_from_entities(storage_context_entities: List[DotDict]):
    for entity in storage_context_entities:

        is_relation = isinstance(entity, FlatRelation)
        entity_properties = _compute_properties_from_traits(entity, is_relation)

        _observer_pk = entity[FlatRelation.OBSERVER_PK]
        for row in entity_properties:
            # TODO this can be an issue as TS is added late in the pipeline
            row[FlatEntityProperty.TS] = now_in_utc()
            row[FlatEntityProperty.OBSERVER_PK] = _observer_pk

            # This hash will keep historic values as well as it hashes value
            row[FlatEntityProperty.PROPERTY_ID] = md5(
                f"{row[FlatEntityProperty.OBSERVER_PK]}"
                f"-{row[FlatEntityProperty.PK]}"
                f"-{row[FlatEntityProperty.TYPE]}"
                f"-{row[FlatEntityProperty.VALUE]}"
            )
            yield row

        # --- Yield addition data

        if isinstance(entity, FlatRelation):

            # Yield label for realtion
            label = entity.get(FlatRelation.REL_LABEL, None)
            if label:
                row = {
                    FlatEntityProperty.PK: entity['entity.pk'],
                    FlatEntityProperty.ID: entity['entity.id'],
                    FlatEntityProperty.TYPE: entity['entity.type'],

                    FlatEntityProperty.NAME: "_label",
                    FlatEntityProperty.VALUE: label,
                    FlatEntityProperty.TEXT: label,
                    FlatEntityProperty.NUMBER: None,
                    FlatEntityProperty.VECTOR: None,
                    FlatEntityProperty.TS: now_in_utc(),

                    FlatEntityProperty._IS_RELATION: True,

                    FlatEntityProperty.OBSERVER_PK: entity[ObservationEntity.OBSERVER_PK]
                }

                row[FlatEntityProperty.PROPERTY_ID] = md5(
                    f"{row[FlatEntityProperty.OBSERVER_PK]}"
                    f"-{row[FlatEntityProperty.PK]}"
                    f"-{row[FlatEntityProperty.TYPE]}"
                    f"-{row[FlatEntityProperty.VALUE]}"
                )
                yield row

            # Yield type for relation
            event_type = entity.get(FlatRelation.REL_TYPE, None)
            if event_type:
                row = {
                    FlatEntityProperty.PK: entity['entity.pk'],
                    FlatEntityProperty.ID: entity['entity.id'],
                    FlatEntityProperty.TYPE: entity['entity.type'],

                    FlatEntityProperty.NAME: "_type",
                    FlatEntityProperty.VALUE: event_type,
                    FlatEntityProperty.TEXT: event_type,
                    FlatEntityProperty.NUMBER: None,
                    FlatEntityProperty.VECTOR: None,
                    FlatEntityProperty.TS: now_in_utc(),

                    FlatEntityProperty._IS_RELATION: True,

                    FlatEntityProperty.OBSERVER_PK: entity[ObservationEntity.OBSERVER_PK]
                }

                row[FlatEntityProperty.PROPERTY_ID] = md5(
                    f"{row[FlatEntityProperty.OBSERVER_PK]}"
                    f"-{row[FlatEntityProperty.PK]}"
                    f"-{row[FlatEntityProperty.TYPE]}"
                    f"-{row[FlatEntityProperty.VALUE]}"
                )
                yield row

        elif isinstance(entity, ObservationEntity):

            # Yield label for entity
            label = entity.get(ObservationEntity.ENTITY_LABEL, None)
            if label:
                row = {
                    FlatEntityProperty.PK: entity['entity.pk'],
                    FlatEntityProperty.ID: entity['entity.id'],
                    FlatEntityProperty.TYPE: entity['entity.type'],

                    FlatEntityProperty.NAME: "_label",
                    FlatEntityProperty.VALUE: label,
                    FlatEntityProperty.TEXT: label,
                    FlatEntityProperty.NUMBER: None,
                    FlatEntityProperty.VECTOR: None,
                    FlatEntityProperty.TS: now_in_utc(),

                    FlatEntityProperty.OBSERVER_PK: entity[ObservationEntity.OBSERVER_PK]
                }

                row[FlatEntityProperty.PROPERTY_ID] = md5(
                    f"{row[FlatEntityProperty.OBSERVER_PK]}"
                    f"-{row[FlatEntityProperty.PK]}"
                    f"-{row[FlatEntityProperty.TYPE]}"
                    f"-{row[FlatEntityProperty.VALUE]}"
                )
                yield row
