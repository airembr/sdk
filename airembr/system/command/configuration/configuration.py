from typing import Optional

from airembr.model.metadata.sys_configuration import Configuration
from airembr.system.adapter.metadata.mysql.mapping.configuration_mapping import map_to_configuration
from airembr.system.adapter.metadata.mysql.service.configuration_service import ConfigurationService
from airembr.system.command.configuration.errors import ConfigurationError
from airembr.system.preconfig.setup_configuration import available_configuration_list

cs = ConfigurationService()


async def get_configuration(configuration_id: str) -> Configuration:
    record = await cs.load_by_id(configuration_id)
    if not record.exists():
        raise ConfigurationError(f"Configuration with ID {configuration_id} not found.", 404)

    return record.map_to_object(map_to_configuration)


async def list_defined_configuration(query: Optional[str], limit: int):
    return await cs.load_all(search=query, limit=limit)


async def add_configuration(config: Configuration):
    return await cs.upsert(config)


async def delete_configuration(configuration_id: str):
    """
    Deletes configuration from the database
    """
    return await cs.delete_by_id(configuration_id)


async def list_configuration_types() -> dict:
    return {
        "total": len(available_configuration_list),
        "result": list(available_configuration_list.values())
    }
