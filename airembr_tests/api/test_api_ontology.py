from uuid import uuid4


def _payload(ontology_id: str, name: str = "Test Ontology") -> dict:
    return {"id": ontology_id, "name": name}


def test_api_ontology_create_and_read(client):
    ontology_id = f"test-ontology-{uuid4()}"

    assert client.post("/v1/ontology", json=_payload(ontology_id)).status_code == 200

    response = client.get(f"/v1/ontology/{ontology_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == ontology_id
    assert body["name"] == "Test Ontology"


def test_api_ontology_list_contains_created(client):
    ontology_id = f"test-ontology-{uuid4()}"
    client.post("/v1/ontology", json=_payload(ontology_id))

    response = client.get("/v1/ontologies")
    assert response.status_code == 200
    assert ontology_id in response.text


def test_api_ontology_delete(client):
    ontology_id = f"test-ontology-{uuid4()}"
    client.post("/v1/ontology", json=_payload(ontology_id))

    assert client.delete(f"/v1/ontology/{ontology_id}").status_code == 200

    response = client.get(f"/v1/ontology/{ontology_id}")
    assert response.status_code == 404
    assert response.json() is None


def test_api_ontology_get_missing_returns_404(client):
    response = client.get(f"/v1/ontology/test-ontology-{uuid4()}")
    assert response.status_code == 404
