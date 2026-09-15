from uuid import uuid4


def _payload(embedding_id: str, name: str = "Test Embedding Setting") -> dict:
    return {
        "id": embedding_id,
        "name": name,
        "event_type": {"id": "evt-1", "name": "Event"},
        "source": {"id": "src-1", "name": "Source"},
    }


def test_api_embedding_setting_create_and_read(client):
    embedding_id = f"test-embedding-{uuid4()}"

    assert client.post("/v1/embedding-setting", json=_payload(embedding_id)).status_code == 200

    response = client.get(f"/v1/embedding-setting/{embedding_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == embedding_id
    assert body["name"] == "Test Embedding Setting"


def test_api_embedding_setting_delete(client):
    embedding_id = f"test-embedding-{uuid4()}"
    client.post("/v1/embedding-setting", json=_payload(embedding_id))

    assert client.delete(f"/v1/embedding-setting/{embedding_id}").status_code == 200

    response = client.get(f"/v1/embedding-setting/{embedding_id}")
    assert response.status_code == 200
    assert response.json() is None


def test_api_embedding_setting_get_missing_returns_none(client):
    response = client.get(f"/v1/embedding-setting/test-embedding-{uuid4()}")
    assert response.status_code == 200
    assert response.json() is None
