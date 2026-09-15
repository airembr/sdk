from uuid import uuid4


def _payload(segment_id: str, name: str = "Test Segment") -> dict:
    return {"id": segment_id, "name": name, "entity_type": "person"}


def test_api_segment_create_and_read(client):
    segment_id = f"test-segment-{uuid4()}"

    assert client.post("/v1/segment", json=_payload(segment_id)).status_code == 200

    response = client.get(f"/v1/segment/{segment_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == segment_id
    assert body["name"] == "Test Segment"


def test_api_segment_list_contains_created(client):
    segment_id = f"test-segment-{uuid4()}"
    client.post("/v1/segment", json=_payload(segment_id))

    response = client.get("/v1/segments")
    assert response.status_code == 200
    assert segment_id in response.text


def test_api_segment_delete(client):
    segment_id = f"test-segment-{uuid4()}"
    client.post("/v1/segment", json=_payload(segment_id))

    assert client.delete(f"/v1/segment/{segment_id}").status_code == 200

    response = client.get(f"/v1/segment/{segment_id}")
    assert response.status_code == 200
    assert response.json() is None
