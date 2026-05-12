from typing import Optional, List, Tuple, Generator

from airembr.model.entity_object import EntityObject, EntityPropertyPayload, \
    EntityPropertyStitchPayload
from airembr.system.adapter.metadata.mysql.mapping.entity_object_mapping import map_to_entity_object
from airembr.system.adapter.metadata.mysql.service.entity_object_service import EntityObjectService
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from sqlalchemy.orm import class_mapper

eos = EntityObjectService()


def _to_dict(model_instance):
    return {
        column.key: getattr(model_instance, column.key)
        for column in class_mapper(model_instance.__class__).columns
    }


def _records(records: SelectResult) -> Tuple[List[EntityObject], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_entity_object)), records.count()


def _convert_to_properties(entity_property_records):
    for num, row in enumerate(entity_property_records):
        row['id'] = num
        obj = EntityPropertyPayload(**row)
        yield obj


def _convert_to_stitches(entity_stitches_records):
    for row in entity_stitches_records:
        obj = EntityPropertyStitchPayload(**row)
        yield obj


async def load_all(query=None, limit=None, start=None) -> Tuple[List[EntityObject], int]:
    result = await eos.load_all(search=query, limit=limit, offset=start)
    return _records(result)


async def load_all_records(query=None, limit=None, start=None) -> Generator[EntityObject, None, None]:
    records = await eos.load_all(search=query, limit=limit, offset=start)
    return records.map_to_objects(map_to_entity_object)


async def load_by_id(entity_object: str) -> Optional[EntityObject]:
    record = await eos.load_by_id(entity_object)
    if not record.exists():
        return None
    return record.map_to_object(map_to_entity_object)


async def load_all_with_tables() -> Optional[Generator[EntityObject, None, None]]:
    record = await eos.load_all_with_table()
    if not record.exists():
        return None
    return record.map_to_objects(map_to_entity_object)


async def load_entity_type_by_id(entity_type_id: str) -> Optional[EntityObject]:
    entity_object_record = await eos.load_by_id(entity_type_id)
    if not entity_object_record:
        return None
    return entity_object_record.map_to_object(map_to_entity_object)


async def load_entity_object_by_type(entity_type: str, only_enabled: bool = False) -> Optional[EntityObject]:
    entity_object_record = await eos.load_by_type(entity_type.lower(), only_enabled)
    return entity_object_record.map_to_object(map_to_entity_object)


async def load_enabled(limit: Optional[int] = None) -> Generator[EntityObject, None, None]:
    records = await eos.load_enabled(limit)
    return records.map_to_objects(map_to_entity_object)


async def load_entity_types_2():
    records = await eos.load_enabled()
    return {row.type for row in records.map_to_objects(map_to_entity_object)}


async def delete_by_id(entity_object: str):
    await eos.delete_by_id(entity_object)


async def insert(entity_object: EntityObject):
    return await eos.insert(entity_object)
