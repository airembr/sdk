from dagor.interface.workflow.entrypoint import load_workflow


async def get_workflow(workflow_id: str):
    return await load_workflow(workflow_id)