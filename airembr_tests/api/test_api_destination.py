from uuid import uuid4


def _payload(destination_id: str, name: str = "Test Destination") -> dict:
    return {
        "id": destination_id,
        "name": name,
        "destination": {"package": "some.module.SomeClass"},
        "resource": {"id": "res-1", "type": "workflow"},
        "source": {"id": "src-1", "name": "Source"},
        "trigger": {"type": {"id": "trig-1", "name": "Trigger"}},
    }


def test_api_destination_create_and_read(client):
    destination_id = f"test-destination-{uuid4()}"

    assert client.post("/v1/destination", json=_payload(destination_id)).status_code == 200

    response = client.get(f"/v1/destination/{destination_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == destination_id
    assert body["name"] == "Test Destination"


def test_api_destination_list_contains_created(client):
    destination_id = f"test-destination-{uuid4()}"
    client.post("/v1/destination", json=_payload(destination_id))

    response = client.get("/v1/destinations")
    assert response.status_code == 200
    assert destination_id in response.text


def test_api_destination_delete(client):
    destination_id = f"test-destination-{uuid4()}"
    client.post("/v1/destination", json=_payload(destination_id))

    assert client.delete(f"/v1/destination/{destination_id}").status_code == 200

    response = client.get(f"/v1/destination/{destination_id}")
    assert response.status_code == 404
    assert response.json() is None


def test_api_destination_get_missing_returns_404(client):
    response = client.get(f"/v1/destination/test-destination-{uuid4()}")
    assert response.status_code == 404
