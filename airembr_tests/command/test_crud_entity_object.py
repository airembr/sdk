import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext, get_context
from airembr.model.entity_object import EntityObject
from airembr.system.command.v1.meta.entity_object.entity_object import (
    save_entity_object,
    get_entity_object_payload,
    delete_entity_object,
)


def _make_entity_object(entity_type: str) -> EntityObject:
    # save_entity_object's mapper recomputes id as f"{type}-{tenant}",
    # ignoring whatever id is passed in - so id is left unset here.
    return EntityObject(id="unused", type=entity_type, lock=False, stitches=[])


def test_crud_entity_object_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            entity_type = f"test-entity-object-{uuid4().hex}"
            await save_entity_object(_make_entity_object(entity_type))
            entity_type_id = f"{entity_type}-{get_context().tenant}"

            fetched = await get_entity_object_payload(entity_type_id)

            assert fetched is not None
            assert fetched.id == entity_type_id
            assert fetched.type == entity_type
        asyncio.run(scenario())


def test_crud_entity_object_delete():
    with ServerContext(Context()):
        async def scenario():
            entity_type = f"test-entity-object-{uuid4().hex}"
            await save_entity_object(_make_entity_object(entity_type))
            entity_type_id = f"{entity_type}-{get_context().tenant}"

            await delete_entity_object(entity_type_id)

            assert await get_entity_object_payload(entity_type_id) is None
        asyncio.run(scenario())
