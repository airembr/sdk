from uuid import uuid4


def _payload(validator_id: str, name: str = "Test Validator") -> dict:
    return {
        "id": validator_id,
        "name": name,
        "event_type": "test-event",
        "entity_type": "person",
        "validation": {"json_schema": {}},
    }


def test_api_validator_create_and_read(client):
    validator_id = f"test-validator-{uuid4()}"

    response = client.post("/v1/validator", json=_payload(validator_id))
    assert response.status_code == 200
    assert response.json() == {"saved": True}

    get_response = client.get(f"/v1/validator/{validator_id}")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["id"] == validator_id
    assert body["name"] == "Test Validator"


def test_api_validator_delete(client):
    validator_id = f"test-validator-{uuid4()}"
    client.post("/v1/validator", json=_payload(validator_id))

    assert client.delete(f"/v1/validator/{validator_id}").status_code == 200

    response = client.get(f"/v1/validator/{validator_id}")
    assert response.status_code == 404


def test_api_validator_get_missing_returns_404(client):
    response = client.get(f"/v1/validator/test-validator-{uuid4()}")
    assert response.status_code == 404
