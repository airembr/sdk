from uuid import uuid4

from airembr.system.logging.log_handler import get_logger
from airembr.system.adapter.metadata.mysql.service.version_service import VersionService
from airembr.system.process.preconfig.setup_bridges import os_default_bridges
from airembr.system.adapter.metadata.mysql.service.bridge_service import BridgeService
from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.model.system.installer.credentials import Credentials
from airembr.model.metadata.sys_user import User
from airembr.sdk.storage.metadata.proxy.database_service_proxy import DatabaseServiceProxy
from airembr.model.system.context import ServerContext, get_context
from airembr.core.singleton import Singleton
from airembr.system.adapter.metadata.location import get_md_sql_view_folder

logger = get_logger(__name__)

class MetaDataInstallManager(metaclass=Singleton):

    def __init__(self):
        self.ds = DatabaseServiceProxy()

    async def install_metadata_database(self, credentials: Credentials, version):
        await self.ds.bootstrap()

        # Install global default bridges
        await BridgeService.bootstrap(default_bridges=os_default_bridges)

        # Install views
        await self.ds.create_views(sqls=[
            'sys_v_destination_resource.sql'
        ], folder=get_md_sql_view_folder())

        # TODO context may not be needed - check
        # Install staging
        with ServerContext(get_context().switch_context(production=False)):

            # Add admin
            us = UserService()
            admins = await us.load_by_role('admin')

            if credentials.needs_admin and len(admins) == 0:
                user = User(
                    id=str(uuid4()),
                    password=User.encode_password(credentials.password),
                    roles=['admin', 'maintainer'],
                    email=credentials.username,
                    name="Default Admin",
                    enabled=True
                )

                # Install version in Metadata

                vs = VersionService()
                await vs.upsert(version)

                # Add admin
                us = UserService()
                await us.insert_if_none(user)

                return True

            else:
                logger.warning("There is at least one admin account. New admin account not created.")
                return True