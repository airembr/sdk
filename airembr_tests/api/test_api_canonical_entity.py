from uuid import uuid4


def _entity_payload(entity_id: str, name: str) -> dict:
    return {"id": entity_id, "name": name, "ontology_id": "onto-1"}


def _property_payload(prop_id: str) -> dict:
    return {"id": prop_id, "name": "serial_number", "type": "STRING"}


def test_api_canonical_entity_create_and_read(client):
    entity_id = f"test-canonical-entity-{uuid4()}"
    name = f"DEVICE-{entity_id}"

    assert client.post("/v1/canonical-entity", json=_entity_payload(entity_id, name)).status_code == 200

    response = client.get(f"/v1/canonical-entity/{entity_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == entity_id
    assert body["name"] == name


def test_api_canonical_entity_list_contains_created(client):
    entity_id = f"test-canonical-entity-{uuid4()}"
    client.post("/v1/canonical-entity", json=_entity_payload(entity_id, f"DEVICE-{entity_id}"))

    response = client.get("/v1/canonical-entities")
    assert response.status_code == 200
    assert entity_id in response.text


def test_api_canonical_entity_delete(client):
    entity_id = f"test-canonical-entity-{uuid4()}"
    client.post("/v1/canonical-entity", json=_entity_payload(entity_id, f"DEVICE-{entity_id}"))

    assert client.delete(f"/v1/canonical-entity/{entity_id}").status_code == 200

    response = client.get(f"/v1/canonical-entity/{entity_id}")
    assert response.status_code == 404
    assert response.json() is None


def test_api_canonical_entity_property_create_and_read(client):
    entity_id = f"test-canonical-entity-{uuid4()}"
    prop_id = f"test-canonical-entity-property-{uuid4()}"

    response = client.post(f"/v1/canonical-entity/{entity_id}/property", json=_property_payload(prop_id))
    assert response.status_code == 200

    get_response = client.get(f"/v1/canonical-entity-property/{prop_id}")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["id"] == prop_id
    assert body["name"] == "serial_number"


def test_api_canonical_entity_property_delete(client):
    entity_id = f"test-canonical-entity-{uuid4()}"
    prop_id = f"test-canonical-entity-property-{uuid4()}"
    client.post(f"/v1/canonical-entity/{entity_id}/property", json=_property_payload(prop_id))

    assert client.delete(f"/v1/canonical-entity-property/{prop_id}").status_code == 200

    response = client.get(f"/v1/canonical-entity-property/{prop_id}")
    assert response.status_code == 404
    assert response.json() is None
