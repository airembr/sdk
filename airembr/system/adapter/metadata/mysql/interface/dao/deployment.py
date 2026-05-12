from airembr.system.adapter.metadata.mysql.service.deployment_service import DeploymentService

ds = DeploymentService()


async def deploy(table_name: str, id: str, deploy: bool = True) -> bool:
    return await ds.deploy(table_name, id, deploy)

