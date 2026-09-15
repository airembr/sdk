from uuid import uuid4


def _payload(configuration_id: str, name: str = "Test Config") -> dict:
    return {"id": configuration_id, "name": name, "config": {"key": "value"}}


def test_api_configuration_create_and_read(client):
    configuration_id = f"test-configuration-{uuid4()}"

    assert client.post("/v1/configuration", json=_payload(configuration_id)).status_code == 200

    response = client.get(f"/v1/configuration/{configuration_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == configuration_id
    assert body["name"] == "Test Config"


def test_api_configuration_list_contains_created(client):
    configuration_id = f"test-configuration-{uuid4()}"
    client.post("/v1/configuration", json=_payload(configuration_id))

    response = client.get("/v1/configurations")
    assert response.status_code == 200
    assert configuration_id in response.text


def test_api_configuration_delete(client):
    configuration_id = f"test-configuration-{uuid4()}"
    client.post("/v1/configuration", json=_payload(configuration_id))

    assert client.delete(f"/v1/configuration/{configuration_id}").status_code == 200

    response = client.get(f"/v1/configuration/{configuration_id}")
    assert response.status_code == 404


def test_api_configuration_get_missing_returns_404(client):
    response = client.get(f"/v1/configuration/test-configuration-{uuid4()}")
    assert response.status_code == 404
