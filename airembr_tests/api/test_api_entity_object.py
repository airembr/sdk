from uuid import uuid4

from airembr.model.system.context import Context, ServerContext, get_context


def _entity_type_id(entity_type: str) -> str:
    # save_entity_object's mapper recomputes the id as f"{type}-{tenant}",
    # ignoring whatever id is sent in the payload.
    with ServerContext(Context()):
        return f"{entity_type}-{get_context().tenant}"


def _payload(entity_type: str) -> dict:
    return {"id": "unused", "type": entity_type, "lock": False, "stitches": []}


def test_api_entity_object_create_and_read(client):
    entity_type = f"test-entity-object-{uuid4().hex}"

    assert client.post("/v1/entity-object", json=_payload(entity_type)).status_code == 200

    entity_type_id = _entity_type_id(entity_type)
    response = client.get(f"/v1/entity-object/{entity_type_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == entity_type_id
    assert body["type"] == entity_type


def test_api_entity_object_delete(client):
    entity_type = f"test-entity-object-{uuid4().hex}"
    client.post("/v1/entity-object", json=_payload(entity_type))
    entity_type_id = _entity_type_id(entity_type)

    assert client.delete(f"/v1/entity-object/{entity_type_id}").status_code == 200

    response = client.get(f"/v1/entity-object/{entity_type_id}")
    assert response.status_code == 200
    assert response.json() is None
