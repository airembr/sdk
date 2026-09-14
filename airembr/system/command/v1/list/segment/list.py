from typing import Optional

from airembr.system.adapter.metadata.mysql.interface import segment_dao


async def list_segments(query: Optional[str], start: int, limit: int):
    return await segment_dao.load_all(query, limit, start)


async def list_segments_meta(query: Optional[str], start: int, limit: int):
    return await segment_dao.load_all_raw(query, limit, start)
