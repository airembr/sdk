from uuid import uuid4


def _payload(source_id: str, name: str = "Test Source") -> dict:
    return {
        "id": source_id,
        "name": name,
        "type": ["webhook"],
        "bridge": {"id": "bridge-1", "name": "Bridge"},
    }


def test_api_source_create_and_read(client):
    source_id = f"test-source-{uuid4()}"

    assert client.post("/v1/source", json=_payload(source_id)).status_code == 200

    response = client.get(f"/v1/source/{source_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == source_id
    assert body["name"] == "Test Source"


def test_api_source_list_contains_created(client):
    source_id = f"test-source-{uuid4()}"
    client.post("/v1/source", json=_payload(source_id))

    response = client.get("/v1/sources")
    assert response.status_code == 200
    assert source_id in response.text


def test_api_source_delete(client):
    source_id = f"test-source-{uuid4()}"
    client.post("/v1/source", json=_payload(source_id))

    assert client.delete(f"/v1/source/{source_id}").status_code == 200

    response = client.get(f"/v1/source/{source_id}")
    assert response.status_code == 404
    assert response.json() is None


def test_api_source_get_missing_returns_404(client):
    response = client.get(f"/v1/source/test-source-{uuid4()}")
    assert response.status_code == 404
