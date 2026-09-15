from uuid import uuid4


def _payload(event_type: str, name: str = "Test Mapping") -> dict:
    return {"name": name, "event_type": event_type, "entity_type": "person"}


def test_api_payload_mapping_create_and_read(client):
    event_type = f"test-payload-mapping-{uuid4()}"

    assert client.post("/v1/payload-mapping", json=_payload(event_type)).status_code == 200

    response = client.get(f"/v1/payload-mapping/{event_type}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == event_type
    assert body["name"] == "Test Mapping"


def test_api_payload_mapping_delete(client):
    event_type = f"test-payload-mapping-{uuid4()}"
    client.post("/v1/payload-mapping", json=_payload(event_type))

    assert client.delete(f"/v1/payload-mapping/{event_type}").status_code == 200

    response = client.get(f"/v1/payload-mapping/{event_type}")
    assert response.status_code == 404


def test_api_payload_mapping_get_missing_returns_404(client):
    response = client.get(f"/v1/payload-mapping/test-payload-mapping-{uuid4()}")
    assert response.status_code == 404
