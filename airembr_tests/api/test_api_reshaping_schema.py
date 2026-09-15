from uuid import uuid4


def _payload(reshaping_id: str, name: str = "Test Reshaping Schema") -> dict:
    return {
        "id": reshaping_id,
        "name": name,
        "event_type": "test-event",
        "entity_type": "person",
        "event_source": {"id": "src-1", "name": "Source"},
        "reshaping": {"reshape_schema": {}},
    }


def test_api_reshaping_schema_create_and_read(client):
    reshaping_id = f"test-reshaping-{uuid4()}"

    response = client.post("/v1/reshaping-schema", json=_payload(reshaping_id))
    assert response.status_code == 200
    assert response.json() == {"saved": True}

    get_response = client.get(f"/v1/reshaping-schema/{reshaping_id}")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["id"] == reshaping_id
    assert body["name"] == "Test Reshaping Schema"


def test_api_reshaping_schema_delete(client):
    reshaping_id = f"test-reshaping-{uuid4()}"
    client.post("/v1/reshaping-schema", json=_payload(reshaping_id))

    assert client.delete(f"/v1/reshaping-schema/{reshaping_id}").status_code == 200

    response = client.get(f"/v1/reshaping-schema/{reshaping_id}")
    assert response.status_code == 404


def test_api_reshaping_schema_get_missing_returns_404(client):
    response = client.get(f"/v1/reshaping-schema/test-reshaping-{uuid4()}")
    assert response.status_code == 404
