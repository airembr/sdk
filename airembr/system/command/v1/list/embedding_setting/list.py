from typing import Optional, Tuple

from airembr.system.adapter.metadata.mysql.interface import embedding_setting_dao


async def list_embedding_settings(query: Optional[str], start: int, limit: int) -> Tuple[list, int]:
    return await embedding_setting_dao.load_all(query, limit, start)
