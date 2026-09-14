from typing import Optional

from airembr.system.adapter.metadata.mysql.service.configuration_service import ConfigurationService
from airembr.system.preconfig.setup_configuration import available_configuration_list

cs = ConfigurationService()


async def list_defined_configuration(query: Optional[str], limit: int):
    return await cs.load_all(search=query, limit=limit)


async def list_configuration_types() -> dict:
    return {
        "total": len(available_configuration_list),
        "result": list(available_configuration_list.values())
    }
