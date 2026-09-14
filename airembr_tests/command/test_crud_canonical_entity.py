import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_canonical_entity import CanonicalEntity, CanonicalEntityProperty, PropertyType
from airembr.system.command.v1.meta.canonical_entity.entities import (
    save_canonical_entity,
    get_canonical_entity,
    delete_canonical_entity,
)
from airembr.system.command.v1.meta.canonical_entity.properties import (
    save_entity_property,
    get_entity_property,
    delete_entity_property,
)


def test_crud_canonical_entity_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            entity_id = f"test-canonical-entity-{uuid4()}"
            entity = CanonicalEntity(id=entity_id, name=f"DEVICE-{entity_id}", ontology_id="onto-1")

            created = await save_canonical_entity(entity)
            fetched = await get_canonical_entity(entity_id)

            assert created.id == entity_id
            assert fetched is not None
            assert fetched.id == entity_id
            assert fetched.name == f"DEVICE-{entity_id}"
        asyncio.run(scenario())


def test_crud_canonical_entity_delete():
    with ServerContext(Context()):
        async def scenario():
            entity_id = f"test-canonical-entity-{uuid4()}"
            entity = CanonicalEntity(id=entity_id, name=f"DEVICE-{entity_id}", ontology_id="onto-1")
            await save_canonical_entity(entity)

            result = await delete_canonical_entity(entity_id)

            assert result is True
            assert await get_canonical_entity(entity_id) is None
        asyncio.run(scenario())


def test_crud_canonical_entity_property_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            entity_id = f"test-canonical-entity-{uuid4()}"
            prop_id = f"test-canonical-entity-property-{uuid4()}"
            prop = CanonicalEntityProperty(id=prop_id, name="serial_number", type=PropertyType.STRING)

            created = await save_entity_property(entity_id, prop)
            fetched = await get_entity_property(prop_id)

            assert created.canonical_entity_id == entity_id
            assert fetched is not None
            assert fetched.id == prop_id
            assert fetched.name == "serial_number"
            assert fetched.canonical_entity_id == entity_id
        asyncio.run(scenario())


def test_crud_canonical_entity_property_delete():
    with ServerContext(Context()):
        async def scenario():
            entity_id = f"test-canonical-entity-{uuid4()}"
            prop_id = f"test-canonical-entity-property-{uuid4()}"
            prop = CanonicalEntityProperty(id=prop_id, name="serial_number", type=PropertyType.STRING)
            await save_entity_property(entity_id, prop)

            result = await delete_entity_property(prop_id)

            assert result is True
            assert await get_entity_property(prop_id) is None
        asyncio.run(scenario())
