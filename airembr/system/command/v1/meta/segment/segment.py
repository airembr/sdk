from airembr.model.metadata.sys_ent_segment import EntitySegment
from airembr.system.adapter.metadata.mysql.interface import segment_dao


async def save_segment(segment: EntitySegment):
    await segment_dao.insert(segment)


async def get_segment(segment_id: str):
    return await segment_dao.load_by_id(segment_id)


async def delete_segment(segment_id: str):
    return await segment_dao.delete_by_id(segment_id)
