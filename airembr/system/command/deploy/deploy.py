from airembr.system.adapter.metadata.mysql.interface import deployment_dao


async def set_deployment(table_name: str, entity_id: str, deploy: bool):
    return await deployment_dao.deploy(table_name, entity_id, deploy=deploy)
