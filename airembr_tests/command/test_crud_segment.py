import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_ent_segment import EntitySegment
from airembr.system.command.v1.meta.segment.segment import save_segment, get_segment, delete_segment


def test_crud_segment_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            segment_id = f"test-segment-{uuid4()}"
            await save_segment(EntitySegment(id=segment_id, name="Test Segment", entity_type="person"))

            fetched = await get_segment(segment_id)

            assert fetched is not None
            assert fetched.id == segment_id
            assert fetched.name == "Test Segment"
        asyncio.run(scenario())


def test_crud_segment_delete():
    with ServerContext(Context()):
        async def scenario():
            segment_id = f"test-segment-{uuid4()}"
            await save_segment(EntitySegment(id=segment_id, name="Test Segment", entity_type="person"))

            await delete_segment(segment_id)

            assert await get_segment(segment_id) is None
        asyncio.run(scenario())
