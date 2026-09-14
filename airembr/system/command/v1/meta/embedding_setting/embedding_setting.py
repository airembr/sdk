from typing import Optional

from airembr.model.metadata.sys_embedding_setting import EmbeddingSetting
from airembr.system.adapter.metadata.mysql.interface import embedding_setting_dao


async def get_embedding_setting(embedding_id: str) -> Optional[EmbeddingSetting]:
    return await embedding_setting_dao.load_by_id(embedding_id)


async def save_embedding_setting(embedding: EmbeddingSetting):
    await embedding_setting_dao.insert(embedding)


async def delete_embedding_setting(embedding_id: str):
    return await embedding_setting_dao.delete_by_id(embedding_id)
