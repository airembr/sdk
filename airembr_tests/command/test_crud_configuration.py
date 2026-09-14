import asyncio
from uuid import uuid4

import pytest

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_configuration import Configuration
from airembr.system.command.v1.errors.configuration_errors import ConfigurationError
from airembr.system.command.v1.meta.configuration.configuration import (
    add_configuration,
    get_configuration,
    delete_configuration,
)


def test_crud_configuration_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            configuration_id = f"test-configuration-{uuid4()}"
            await add_configuration(Configuration(id=configuration_id, name="Test Config", config={"key": "value"}))

            fetched = await get_configuration(configuration_id)

            assert fetched is not None
            assert fetched.id == configuration_id
            assert fetched.name == "Test Config"
        asyncio.run(scenario())


def test_crud_configuration_delete():
    with ServerContext(Context()):
        async def scenario():
            configuration_id = f"test-configuration-{uuid4()}"
            await add_configuration(Configuration(id=configuration_id, name="Test Config", config={"key": "value"}))

            await delete_configuration(configuration_id)

            with pytest.raises(ConfigurationError):
                await get_configuration(configuration_id)
        asyncio.run(scenario())


def test_crud_configuration_get_missing_raises_404():
    with ServerContext(Context()):
        async def scenario():
            with pytest.raises(ConfigurationError) as exc_info:
                await get_configuration(f"test-configuration-{uuid4()}")
            assert exc_info.value.status_code == 404
        asyncio.run(scenario())
