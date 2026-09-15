from uuid import uuid4

import pytest
from fastapi.exceptions import ResponseValidationError

from airembr.system.preconfig.setup_destination_triggers import DT_EVENT_TRIGGER


def test_api_destination_trigger_get_known_preconfigured_trigger(client):
    response = client.get(f"/v2/destination-trigger/{DT_EVENT_TRIGGER}")
    assert response.status_code == 200
    assert response.json()["id"] == DT_EVENT_TRIGGER


def test_api_destination_trigger_list_contains_known_trigger(client):
    response = client.get("/v1/destination-triggers/meta")
    assert response.status_code == 200
    assert DT_EVENT_TRIGGER in response.text


def test_api_destination_trigger_get_missing_raises_response_validation_error(client):
    # NOTE: the route declares response_model=DestinationTrigger (not Optional),
    # but the command returns None for an unknown id, so FastAPI's response
    # validation itself fails instead of a clean 404. This pins the current
    # (buggy) behavior rather than the desired one.
    with pytest.raises(ResponseValidationError):
        client.get(f"/v2/destination-trigger/test-trigger-{uuid4()}")
