from airembr.system.license.license_verifier import system_license

if system_license.valid:
    from dagor.interface.workflow.entrypoint import load_workflow


    async def get_workflow(workflow_id: str):
        return await load_workflow(workflow_id)