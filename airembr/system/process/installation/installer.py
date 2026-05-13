from dagor.interface.plugin.entrypoint import install_default_plugins

from airembr.model.system.installer.credentials import Credentials
from airembr.system.process.logging.log_handler import get_installation_logger
from airembr.system.adapter.bigdata.big_data_adapter import *
from airembr.system.process.installation.md_install_manager import MetaDataInstallManager

logger = get_installation_logger(__name__)


async def install_system(credentials: Credentials):

    if sys_config.installation_token and sys_config.installation_token != credentials.token:
        raise PermissionError("Installation forbidden. Invalid installation token.")

    admin = await MetaDataInstallManager().install_metadata_database(credentials, version=sys_config.version)

    logger.info(f"Installing plugins on startup")
    await install_default_plugins()

    staging_install_result, production_install_result = await bd_install_adapter.install_big_data_database(credentials)
    staging_install_result['admin'] = admin

    return staging_install_result, production_install_result
