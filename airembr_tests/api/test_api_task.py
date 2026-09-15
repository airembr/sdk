import asyncio
from uuid import uuid4

from airembr.model.system.context import Context, ServerContext
from airembr.system.adapter.metadata.mysql.service.task_service import BackgroundTaskService


def _payload(task_id: str, status: str = "pending") -> dict:
    return {"id": task_id, "name": "Test Task", "task_id": task_id, "type": "import", "status": status}


def _load_task(task_id: str):
    # There is no GET-by-id route for tasks at the API level; verify state
    # through the same service the command layer uses.
    with ServerContext(Context()):
        record = asyncio.run(BackgroundTaskService().load_by_id(task_id))
        return record.map_to_object(lambda row: row)


def test_api_task_create_and_update(client):
    task_id = f"test-task-{uuid4()}"

    assert client.post("/v1/task", json=_payload(task_id, status="pending")).status_code == 200
    assert _load_task(task_id).status == "pending"

    assert client.post("/v1/task", json=_payload(task_id, status="finished")).status_code == 200
    assert _load_task(task_id).status == "finished"


def test_api_task_delete(client):
    task_id = f"test-task-{uuid4()}"
    client.post("/v1/task", json=_payload(task_id))

    assert client.delete(f"/v1/task/{task_id}").status_code == 200
    assert _load_task(task_id) is None
