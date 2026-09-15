import os

os.environ["META_DATA_ADAPTER"] = "sqlite"
os.environ["SQLITE_HOST"] = ""

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_user import User
from airembr.sdk.storage.metadata.proxy.database_service_proxy import DatabaseServiceProxy
from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.system.adapter.metadata.mysql.mapping.user_mapping import map_to_user
from airembr.system.command.auth.token_store import token2user

import airembr_api.endpoint.gui.v1.tools.auth.permissions as permissions_module

# CRUD routers
from airembr_api.endpoint.gui.v1.routes.meta.bridge import crud_endpoint as crud_bridge
from airembr_api.endpoint.gui.v1.routes.meta.canonical_entity import crud_endpoint as crud_canonical_entity
from airembr_api.endpoint.gui.v1.routes.meta.configuration import crud_endpoint as crud_configuration
from airembr_api.endpoint.gui.v1.routes.meta.destination import crud_endpoint as crud_destination
from airembr_api.endpoint.gui.v1.routes.meta.destination_trigger import crud_endpoint as crud_destination_trigger
from airembr_api.endpoint.gui.v1.routes.meta.embedding_setting import crud_endpoint as crud_embedding_setting
from airembr_api.endpoint.gui.v1.routes.meta.entity_object import crud_endpoint as crud_entity_object
from airembr_api.endpoint.gui.v1.routes.meta.ontology import crud_endpoint as crud_ontology
from airembr_api.endpoint.gui.v1.routes.meta.payload_mapping import crud_endpoint as crud_payload_mapping
from airembr_api.endpoint.gui.v1.routes.meta.reshaping_schema import crud_endpoint as crud_reshaping_schema
from airembr_api.endpoint.gui.v1.routes.meta.resource import crud_endpoint as crud_resource
from airembr_api.endpoint.gui.v1.routes.meta.segment import crud_endpoint as crud_segment
from airembr_api.endpoint.gui.v1.routes.meta.settings import crud_endpoint as crud_settings
from airembr_api.endpoint.gui.v1.routes.meta.source import crud_endpoint as crud_source
from airembr_api.endpoint.gui.v1.routes.meta.task import crud_endpoint as crud_task
from airembr_api.endpoint.gui.v1.routes.meta.user import crud_endpoint as crud_user
from airembr_api.endpoint.gui.v1.routes.meta.user_account import crud_endpoint as crud_user_account
from airembr_api.endpoint.gui.v1.routes.meta.validator import crud_endpoint as crud_validator

# List routers
from airembr_api.endpoint.gui.v1.routes.meta.bridge import list_endpoint as list_bridge
from airembr_api.endpoint.gui.v1.routes.meta.canonical_entity import list_endpoint as list_canonical_entity
from airembr_api.endpoint.gui.v1.routes.meta.configuration import list_endpoint as list_configuration
from airembr_api.endpoint.gui.v1.routes.meta.destination import list_endpoint as list_destination
from airembr_api.endpoint.gui.v1.routes.meta.destination_trigger import list_endpoint as list_destination_trigger
from airembr_api.endpoint.gui.v1.routes.meta.ontology import list_endpoint as list_ontology
from airembr_api.endpoint.gui.v1.routes.meta.resource import list_endpoint as list_resource
from airembr_api.endpoint.gui.v1.routes.meta.segment import list_endpoint as list_segment
from airembr_api.endpoint.gui.v1.routes.meta.settings import list_endpoint as list_settings
from airembr_api.endpoint.gui.v1.routes.meta.source import list_endpoint as list_source

# Fixed identity used for every request. Every route is protected by
# Permissions(...), which is bypassed below by patching `authorize`.
FAKE_ADMIN_ID = "test-admin-fixed-id"
FAKE_ADMIN = User(
    id=FAKE_ADMIN_ID,
    password="unused",
    name="Test Admin",
    email="test-admin@example.com",
    roles=["admin", "developer", "marketer", "maintainer"],
    enabled=True,
)


class _FakeCache:
    """Minimal in-process stand-in for the Redis-backed CacheProtocol.

    token2user (auth/token_store.py) is used by several command modules
    (edit_user, preferences, edit_user_account) even when auth itself is
    bypassed. Swapping its backing store avoids requiring a live Redis.
    """

    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value, ex=None, nx: bool = None):
        self._store[key] = value
        return True

    def delete(self, key, skip_tenant: bool = False):
        self._store.pop(key, None)

    def expire(self, key, ttl):
        pass


async def _fake_authorize(token, roles, request_path=""):
    # Re-fetch on every call (rather than returning the fixed FAKE_ADMIN
    # constant) so that endpoints which edit "the calling user" (e.g.
    # user-account, user-preference) observe their own previous writes.
    record = await UserService().load_by_id(FAKE_ADMIN_ID)
    if record.exists():
        return record.map_to_object(map_to_user)
    return FAKE_ADMIN


class _TestContextMiddleware:
    """Stand-in for airembr_api.middleware.context.ContextRequestMiddleware.

    The real middleware pulls in the StarRocks/bigdata adapter stack (for
    save_logs) via a module-level `import *`, which requires the internal
    `srd` package that isn't installed in this SDK-only environment. Only
    the tenant/ServerContext behavior is needed for the metadata DAOs under
    test here, so that part is reproduced directly instead.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket", "https"):
            await self.app(scope, receive, send)
            return

        with ServerContext(Context()):
            await self.app(scope, receive, send)


@pytest.fixture(scope="session", autouse=True)
def bootstrap_metadata_db():
    """Creates the in-memory sqlite schema once per test session and seeds
    the fixed admin user so user_account endpoints (which load/update the
    caller's own row) have something to operate on."""

    token2user._token_memory._cache = _FakeCache()

    with ServerContext(Context()):
        asyncio.run(DatabaseServiceProxy().bootstrap())
        asyncio.run(UserService().upsert(FAKE_ADMIN))


@pytest.fixture(autouse=True)
def _patch_auth(monkeypatch):
    monkeypatch.setattr(permissions_module, "authorize", _fake_authorize)


def _build_api_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(_TestContextMiddleware)

    for module in (
        crud_bridge, crud_canonical_entity, crud_configuration, crud_destination,
        crud_destination_trigger, crud_embedding_setting, crud_entity_object,
        crud_ontology, crud_payload_mapping, crud_reshaping_schema, crud_resource,
        crud_segment, crud_settings, crud_source, crud_task, crud_user,
        crud_user_account, crud_validator,
        list_bridge, list_canonical_entity, list_configuration, list_destination,
        list_destination_trigger, list_ontology,
        list_resource, list_segment, list_settings, list_source,
    ):
        app.include_router(module.router)

    return app


@pytest.fixture(scope="session")
def api_app():
    return _build_api_app()


@pytest.fixture()
def client(api_app):
    with TestClient(api_app, headers={"Authorization": "Bearer test-token"}) as test_client:
        yield test_client
