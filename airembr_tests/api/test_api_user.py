from uuid import uuid4


def _payload(email: str, roles=None) -> dict:
    return {
        "password": "Sup3rSecret!",
        "name": "Test User",
        "email": email,
        "roles": roles or ["user"],
        "enabled": True,
    }


def test_api_user_create_and_read(client):
    email = f"test-user-{uuid4()}@example.com"

    create_response = client.post("/v1/user", json=_payload(email))
    assert create_response.status_code == 200
    user_id = create_response.json()

    response = client.get(f"/v1/user/{user_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == user_id
    assert body["email"] == email
    assert body.get("password") is None


def test_api_user_update(client):
    email = f"test-user-{uuid4()}@example.com"
    user_id = client.post("/v1/user", json=_payload(email)).json()

    response = client.post(f"/v1/user/{user_id}", json=_payload(email, roles=["user", "editor"]))
    assert response.status_code == 200
    assert response.json() == {"inserted": True}

    fetched = client.get(f"/v1/user/{user_id}").json()
    assert "editor" in fetched["roles"]


def test_api_user_delete(client):
    email = f"test-user-{uuid4()}@example.com"
    user_id = client.post("/v1/user", json=_payload(email)).json()

    assert client.delete(f"/v1/user/{user_id}").status_code == 200
    assert client.get(f"/v1/user/{user_id}").status_code == 404


def test_api_user_create_duplicate_email_returns_409(client):
    email = f"test-user-{uuid4()}@example.com"
    client.post("/v1/user", json=_payload(email))

    response = client.post("/v1/user", json=_payload(email))
    assert response.status_code == 409


def test_api_user_get_missing_returns_404(client):
    response = client.get(f"/v1/user/test-user-{uuid4()}")
    assert response.status_code == 404


def test_api_user_preference_crud(client):
    # Preferences act on the caller's own user (the fake admin identity
    # injected by the auth bypass), independent of any created user.
    key = f"pref-{uuid4()}"

    assert client.post(f"/v1/user-preference/{key}", json="some-value").status_code == 200

    response = client.get(f"/v1/user-preference/{key}")
    assert response.status_code == 200
    assert response.json() == "some-value"

    assert client.delete(f"/v1/user-preference/{key}").status_code == 200
    assert client.get(f"/v1/user-preference/{key}").status_code == 404
