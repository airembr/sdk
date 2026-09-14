import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.system.named_entity import NamedEntity
from airembr.model.metadata.sys_embedding_setting import EmbeddingSetting
from airembr.system.command.v1.meta.embedding_setting.embedding_setting import (
    save_embedding_setting,
    get_embedding_setting,
    delete_embedding_setting,
)


def _make_embedding_setting(embedding_id: str) -> EmbeddingSetting:
    return EmbeddingSetting(
        id=embedding_id,
        name="Test Embedding Setting",
        event_type=NamedEntity(id="evt-1", name="Event"),
        source=NamedEntity(id="src-1", name="Source"),
    )


def test_crud_embedding_setting_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            embedding_id = f"test-embedding-{uuid4()}"
            await save_embedding_setting(_make_embedding_setting(embedding_id))

            fetched = await get_embedding_setting(embedding_id)

            assert fetched is not None
            assert fetched.id == embedding_id
            assert fetched.name == "Test Embedding Setting"
        asyncio.run(scenario())


def test_crud_embedding_setting_delete():
    with ServerContext(Context()):
        async def scenario():
            embedding_id = f"test-embedding-{uuid4()}"
            await save_embedding_setting(_make_embedding_setting(embedding_id))

            await delete_embedding_setting(embedding_id)

            assert await get_embedding_setting(embedding_id) is None
        asyncio.run(scenario())
