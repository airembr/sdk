from typing import Optional, List, Tuple

from airembr.system.adapter.metadata.mysql.mapping.sys_embedding_setting_mapping import map_to_embedding
from airembr.system.adapter.metadata.mysql.service.embedding_setting_service import EmbeddingService
from airembr.model.metadata.sys_embedding_setting import EmbeddingSetting
from airembr.sdk.storage.metadata.query.select_result import SelectResult
from sqlalchemy.orm import class_mapper

es = EmbeddingService()


def _to_dict(model_instance):
    return {
        column.key: getattr(model_instance, column.key)
        for column in class_mapper(model_instance.__class__).columns
    }


def _records(records: SelectResult) -> Tuple[List[EmbeddingSetting], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_embedding)), records.count()


async def load_all_raw(query=None, limit=None, start=None) -> SelectResult:
    return await es.load_all(search=query, limit=limit, offset=start)


async def load_all(query=None, limit=None, start=None) -> Tuple[List[EmbeddingSetting], int]:
    result = await es.load_all(search=query, limit=limit, offset=start)
    return _records(result)


async def load_by_id(embedding_id: str) -> Optional[EmbeddingSetting]:
    record = await es.load_by_id(embedding_id)
    if not record.exists():
        return None
    return record.map_to_object(map_to_embedding)


async def delete_by_id(embedding_id: str):
    await es.delete_by_id(embedding_id)


async def insert(embedding: EmbeddingSetting):
    return await es.insert(embedding)
