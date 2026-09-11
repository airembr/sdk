from airembr.model.api_instance import ApiInstance
from airembr.model.system.context import get_context
from airembr.system.adapter.metadata.mysql.service.version_service import VersionService
from airembr.system.config.sys_config import sys_config
from airembr.system.license.license_verifier import system_license
from airembr.system.process.installation.installation_status import installation_status

vs = VersionService()


async def list_versions():
    return await vs.load_all(limit=100)


async def get_version() -> str:
    return sys_config.version.version


async def get_current_backend_version() -> dict:
    """
    Returns current backend version with previous versions.
    """
    context = get_context()

    version = sys_config.version.model_dump(mode='json')
    version['tag'] = sys_config.image_tag
    version['instance'] = ApiInstance().id
    version['installed'] = await installation_status.get_status()
    version['tenant'] = context.tenant
    if system_license.valid:
        version['license'] = {
            "issued": system_license.issued_at,
            "licensee": system_license.owner,
            "licensor": "Tracardi",
            "expires": system_license.valid_until if system_license.valid_until else "Never",
            "type": "Proprietary"
        }
    else:
        version['license'] = {
            "issued": "n/a",
            "licensee": "Tracardi",
            "licensor": "Tracardi",
            "expires": "Never",
            "type": "Proprietary"
        }

    return version
