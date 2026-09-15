from uuid import uuid4


def _payload(resource_id: str, name: str = "Test Resource") -> dict:
    return {"id": resource_id, "name": name, "type": "database"}


def test_api_resource_create_and_read(client):
    resource_id = f"test-resource-{uuid4()}"

    create_response = client.post("/v1/resource", json=_payload(resource_id))
    assert create_response.status_code == 200

    get_response = client.get(f"/v1/resource/{resource_id}")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["id"] == resource_id
    assert body["name"] == "Test Resource"


def test_api_resource_update(client):
    resource_id = f"test-resource-{uuid4()}"
    client.post("/v1/resource", json=_payload(resource_id))

    update_response = client.post("/v1/resource", json=_payload(resource_id, name="Updated Resource"))
    assert update_response.status_code == 200

    get_response = client.get(f"/v1/resource/{resource_id}")
    assert get_response.json()["name"] == "Updated Resource"


def test_api_resource_list_contains_created(client):
    resource_id = f"test-resource-{uuid4()}"
    client.post("/v1/resource", json=_payload(resource_id))

    list_response = client.get("/v1/resources")
    assert list_response.status_code == 200
    assert resource_id in list_response.text


def test_api_resource_delete(client):
    resource_id = f"test-resource-{uuid4()}"
    client.post("/v1/resource", json=_payload(resource_id))

    delete_response = client.delete(f"/v1/resource/{resource_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/v1/resource/{resource_id}")
    assert get_response.status_code == 200
    assert get_response.json() is None


def test_api_resource_get_missing_returns_none(client):
    response = client.get(f"/v1/resource/test-resource-{uuid4()}")
    assert response.status_code == 200
    assert response.json() is None
