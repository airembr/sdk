from typing import Optional, Union

from airembr.sdk.model.entity import Entity, PrimaryEntity, FlatEntity


def get_entity_id(entity: Union[Optional[Entity], Optional[FlatEntity]], default=None) -> Optional[str]:
    if not isinstance(entity, (Entity, FlatEntity, dict)):
        raise ValueError(f'Can not get id from type {type(entity)}')

    if isinstance(entity, (Entity, FlatEntity)):
        if entity.id is None:
            return default
        return entity.id

    if isinstance(entity, dict):
        return entity.get("id", default)

    return None


def get_entity(entity: Union[Optional[Entity], Optional[FlatEntity]]) -> Optional[Entity]:
    return Entity(id=entity.id) if isinstance(entity, (Entity, FlatEntity)) else None


def get_primary_entity(entity: Optional[PrimaryEntity]) -> Optional[PrimaryEntity]:
    return PrimaryEntity(id=entity.id, primary_id=entity.primary_id) if isinstance(entity, PrimaryEntity) else None
