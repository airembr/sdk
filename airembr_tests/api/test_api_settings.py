from uuid import uuid4


def test_api_settings_list_system_settings(client):
    response = client.get("/v1/system/settings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_api_settings_get_unset_cluster_setting_returns_none(client):
    # Only GET is exercised here: set_cluster_setting broadcasts the change
    # over Redis pub/sub, which isn't available in this DB-only test harness.
    response = client.get(f"/v1/system/cluster-settings/test-setting-{uuid4()}")
    assert response.status_code == 200
    assert response.json() is None
