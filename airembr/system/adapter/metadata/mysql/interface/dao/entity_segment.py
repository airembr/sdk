from typing import Optional, List, Tuple

from airembr.system.adapter.metadata.mysql.service.segment_service import SegmentService

from airembr.system.adapter.metadata.mysql.mapping.sys_ent_segment_mapping import map_to_segment
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from sqlalchemy.orm import class_mapper

from airembr.model.metadata.sys_ent_segment import EntitySegment

ss = SegmentService()


def _to_dict(model_instance):
    return {
        column.key: getattr(model_instance, column.key)
        for column in class_mapper(model_instance.__class__).columns
    }


def _records(records: SelectResult) -> Tuple[List[EntitySegment], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_segment)), records.count()


async def load_all_raw(query=None, limit=None, start=None) -> SelectResult:
    return await ss.load_all(search=query, limit=limit, offset=start)


async def load_all(query=None, limit=None, start=None) -> Tuple[List[EntitySegment], int]:
    result = await ss.load_all(search=query, limit=limit, offset=start)
    return _records(result)


async def load_by_id(segment: str) -> Optional[EntitySegment]:
    record = await ss.load_by_id(segment)
    if not record.exists():
        return None
    return record.map_to_object(map_to_segment)


async def delete_by_id(segment_id: str):
    await ss.delete_by_id(segment_id)


async def insert(segment: EntitySegment):
    return await ss.insert(segment)
