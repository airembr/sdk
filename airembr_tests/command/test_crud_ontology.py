import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_ontology import Ontology
from airembr.system.command.v1.meta.ontology.ontology import save_ontology, get_ontology, delete_ontology


def test_crud_ontology_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            ontology_id = f"test-ontology-{uuid4()}"
            created = await save_ontology(Ontology(id=ontology_id, name="Test Ontology"))

            fetched = await get_ontology(ontology_id)

            assert fetched is not None
            assert fetched.id == created.id
            assert fetched.name == "Test Ontology"
        asyncio.run(scenario())


def test_crud_ontology_delete():
    with ServerContext(Context()):
        async def scenario():
            ontology_id = f"test-ontology-{uuid4()}"
            await save_ontology(Ontology(id=ontology_id, name="Test Ontology"))

            result = await delete_ontology(ontology_id)

            assert result is True
            assert await get_ontology(ontology_id) is None
        asyncio.run(scenario())
