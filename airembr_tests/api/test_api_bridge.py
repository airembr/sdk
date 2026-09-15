import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_bridge import Bridge
from airembr.system.adapter.metadata.mysql.service.bridge_service import BridgeService


def _seed_bridge(bridge_id: str, name: str = "Test Bridge") -> None:
    # There is no create-via-API route for bridges; seed directly through
    # the same service the DAO layer uses, then exercise the read-only API.
    with ServerContext(Context()):
        asyncio.run(BridgeService().insert(Bridge(id=bridge_id, name=name, type="webhook")))


def test_api_bridge_get_by_id(client):
    bridge_id = f"test-bridge-{uuid4()}"
    _seed_bridge(bridge_id)

    response = client.get(f"/v1/bridge/{bridge_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == bridge_id
    assert body["name"] == "Test Bridge"


def test_api_bridge_list_contains_seeded(client):
    bridge_id = f"test-bridge-{uuid4()}"
    _seed_bridge(bridge_id)

    response = client.get("/v1/bridges")
    assert response.status_code == 200
    assert bridge_id in response.text


def test_api_bridge_get_missing_returns_none(client):
    response = client.get(f"/v1/bridge/test-bridge-{uuid4()}")
    assert response.status_code == 200
    assert response.json() is None
