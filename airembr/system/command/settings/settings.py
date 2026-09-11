from typing import List, Dict, Any, Union

from airembr.model.settings import SystemSettings
from airembr.system.adapter.settings.global_settings_service import GlobalSettings
from airembr.system.preconfig.setup_envs import list_system_envs, get_system_envs


async def get_system_settings() -> List[SystemSettings]:
    """
    Lists all system settings
    """
    return await list_system_envs()


def get_system_envs_list() -> Dict[str, Any]:
    """
    Lists all system settings as key value
    """
    return get_system_envs()


async def set_cluster_setting(key: str, value: Union[float, bool, str]) -> bool:
    if value == 'true':
        value = True
    elif value == 'false':
        value = False
    elif value.isnumeric():
        value = float(value)
    return await GlobalSettings().set(key, value)


async def get_cluster_setting(key: str):
    return await GlobalSettings().get(key)
