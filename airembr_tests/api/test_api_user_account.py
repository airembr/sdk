from conftest import FAKE_ADMIN_ID


def test_api_user_account_get_returns_calling_user(client):
    response = client.get("/v1/user-account")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == FAKE_ADMIN_ID
    assert body.get("password") is None


def test_api_user_account_update_name(client):
    response = client.post("/v1/user-account", json={"name": "Updated Admin Name"})
    assert response.status_code == 200
    assert response.json() == {"inserted": True}

    fetched = client.get("/v1/user-account").json()
    assert fetched["name"] == "Updated Admin Name"
