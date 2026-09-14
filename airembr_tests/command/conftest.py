import os

os.environ["META_DATA_ADAPTER"] = "sqlite"
os.environ["SQLITE_HOST"] = ""

import asyncio

import pytest

from airembr.model.system.context import Context, ServerContext
from airembr.sdk.storage.metadata.proxy.database_service_proxy import DatabaseServiceProxy


@pytest.fixture(scope="session", autouse=True)
def bootstrap_metadata_db():
    with ServerContext(Context()):
        asyncio.run(DatabaseServiceProxy().bootstrap())
