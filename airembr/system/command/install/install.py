from typing import Optional

from airembr.model.system.installer.credentials import Credentials
from airembr.system.preconfig.setup_envs import get_system_envs
from airembr.system.process.installation.installation_status import SystemInstallationStatus
from airembr.system.process.installation.installer import install_system


async def check_if_installation_complete() -> SystemInstallationStatus:
    """
    Returns list of missing and updated indices
    """
    status = await SystemInstallationStatus.check()

    status.config = get_system_envs()

    return status


async def install(credentials: Optional[Credentials]):
    return await install_system(credentials)
